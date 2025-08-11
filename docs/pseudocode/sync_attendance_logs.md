### Phase 4 – كتابة الوصفة (Pseudo‑code) — مزامنة بيانات الحضور

🎯 الهدف
تحويل مخطط تدفق "مزامنة بيانات الحضور" إلى كود زائف (Pseudo-code) واضح ومفصل، جاهز للتحويل إلى Django Management Command أو Celery Task.

المسار: `docs/pseudocode/sync_attendance_logs.md`

```python
# ==============================================================================
# 1. sync_attendance_logs
#   الوصف: مهمة دورية لسحب سجلات الحضور الجديدة من جهاز البصمة FingerTec
#          وتخزينها في قاعدة البيانات المحلية.
#   المدخلات: لا يوجد (تعتمد على الإعدادات المخزنة في النظام).
#   المخرجات: لا يوجد (تُرجع حالة نجاح/فشل فقط).
#   الـ Side-Effects:
#       - إنشاء سجلات جديدة في جدول AttendanceLog.
#       - تحديث timestamp لآخر عملية مزامنة ناجحة.
#       - إرسال تنبيهات في حالة الفشل.
#       - تسجيل تفاصيل العملية في ملفات الـ log.
# ==============================================================================

# هذا الكود سيكون ضمن Django Management Command أو Celery Task

def handle():
    # 1.1 Precondition: Acquire Lock
    #   استخدام قفل (مثل Redis lock أو قفل على مستوى قاعدة البيانات) لمنع
    #   تشغيل أكثر من مهمة مزامنة في نفس الوقت.
    if not lock.acquire(name='sync_attendance_job', blocking=False):
        logger.info("Sync job is already running. Skipping this run.")
        return

    try:
        # 1.2 Get Last Sync Timestamp
        #   جلب آخر timestamp تم تسجيله لعملية مزامنة ناجحة.
        last_sync_time = settings_repo.get('last_sync_timestamp') or "2000-01-01 00:00:00"
        logger.info(f"Starting sync for logs after: {last_sync_time}")

        # 1.3 Main Logic: Connect and Fetch
        try:
            #   الاتصال بالجهاز باستخدام SDK الخاص بـ FingerTec
            device = FingerTecSDK(ip=settings.FINGERTEC_IP, port=settings.FINGERTEC_PORT)
            device.connect()
            new_logs = device.get_new_logs(since=last_sync_time)
        except ConnectionError as e:
            # 1.4 Error Handling: Connection Failure
            logger.error("Failed to connect to FingerTec device.", exc_info=e)
            alerter.send_critical("FingerTec device is offline!")
            return  # إنهاء المهمة هنا

        if not new_logs:
            logger.info("No new attendance logs found.")
            return

        # 1.5 Process Logs
        #   معالجة السجلات ضمن transaction لضمان سلامة البيانات
        new_logs_count = 0
        latest_log_time = None
        with transaction.atomic():
            for log in new_logs:
                # 1.5.1 Parse and Validate Log
                employee_id_from_log = log.get('employee_id')
                timestamp = log.get('timestamp')

                #   البحث عن الموظف في قاعدة بياناتنا
                employee = employee_repo.find_by_external_id(employee_id_from_log)
                if not employee:
                    logger.warning(f"Skipping log for unknown employee ID: {employee_id_from_log}")
                    continue

                #   التحقق من عدم وجود سجل مكرر
                if attendance_repo.exists(employee_id=employee.id, timestamp=timestamp):
                    logger.info(f"Skipping duplicate log for employee {employee.id} at {timestamp}")
                    continue

                # 1.5.2 Save Valid Log
                attendance_repo.create(
                    employee=employee,
                    timestamp=timestamp,
                    log_type=log.get('type'),  # 'IN' or 'OUT'
                    source='FingerTec Device'
                )
                new_logs_count += 1
                latest_log_time = max(latest_log_time, timestamp) if latest_log_time else timestamp

        # 1.6 Post-conditions
        if new_logs_count > 0 and latest_log_time:
            #   تحديث وقت آخر مزامنة ناجحة فقط إذا تمت إضافة سجلات جديدة
            settings_repo.set('last_sync_timestamp', latest_log_time)
            logger.info(f"Successfully synced {new_logs_count} new attendance logs.")

    except Exception as e:
        #   التقاط أي خطأ غير متوقع
        logger.critical("An unexpected error occurred during the sync job.", exc_info=e)
        alerter.send_critical("Attendance sync job failed unexpectedly!")
    finally:
        # 1.7 Release Lock
        #   تحرير القفل في جميع الحالات لضمان أن المهمة التالية يمكن أن تعمل.
        lock.release(name='sync_attendance_job')
```

4.7 – Dev Experience (ما سيضاف إلى المستودع)
- `docs/pseudocode/sync_attendance_logs.md`: الملف أعلاه.
- `apps/attendance/management/commands/sync_logs.py`: ملف Django Management Command (هيكل مبدئي).
- `tests/attendance/test_sync_logs.py`: اختبارات unit/integration للحالات الأساسية.
- `docs/templates/errors.md`: توثيق رسائل الأخطاء والتنبيهات.

ملاحظة استراتيجية
- الكود الزائف يغطي: القفل، معالجة الأخطاء والتنبيهات، المعاملات، والتسجيل.
- جاهز للتحويل إلى كود فعلي ضمن Django/DRF.