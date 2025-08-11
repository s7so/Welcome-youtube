### Phase 3 – رسم خريطة الطريق (Flowchart) — US-03: مزامنة سجلات الحضور

🎯 الهدف
توضيح تدفق عملية سحب بيانات الحضور من جهاز FingerTec بشكل كامل، بما في ذلك سيناريوهات النجاح، الفشل، الاتصال، ومعالجة البيانات، لضمان بناء عملية خلفية (background job) موثوقة وقوية على Django.

3.0 – مخرجات Phase‑3
- docs/flowcharts/us-03-sync-attendance.puml (PlantUML المصدر)
- docs/flowcharts/us-03-sync-attendance.svg (صورة للمراجعة - تُولد من ملف PUML)
- docs/traceability/flow-to-pseudocode.md (جدول الربط بين المخطط والمنطق البرمجي)

3.2 – وصف المخطط (Flowchart)
- Start (يتم تشغيله بواسطة Scheduler، كل 5 دقائق).
- Acquire Lock: منع تشغيل متزامن لنفس المهمة.
  - إذا فشل القفل: Log "Skipping run, previous job still active" → End.
- Get Last Sync Timestamp من قاعدة البيانات.
- Connect to FingerTec Device (IP/Port من الإعدادات).
  - إذا فشل الاتصال: Log Error + Send Alert → Release Lock → End.
- Fetch New Logs منذ آخر وقت مزامنة.
  - لا توجد سجلات جديدة: Log Info → Release Lock → End.
  - توجد سجلات: حلقة عبر كل سجل
    - Parse Log (Employee ID, Timestamp, Type)
    - Find Employee في قاعدة البيانات
      - غير موجود: Log Warning وتخطي السجل
      - موجود: Check Duplicate (employee_id, timestamp)
        - مكرر: Log Info وتخطي
        - غير مكرر: Save داخل معاملة
- بعد إنهاء الحلقة: Update Last Sync Timestamp إلى أحدث وقت سجل
- Commit Transaction
- Release Lock
- End

3.5 – PlantUML (المخطط النصي)
```plantuml
title "Flowchart: Sync Attendance Data"

start
:Acquire Lock for sync job;
if (Lock Acquired?) then (Yes)
  :Get Last Sync Timestamp from DB;
  :Connect to FingerTec Device;
  if (Connection Successful?) then (Yes)
    :Fetch New Logs since last timestamp;
    if (New Logs Found?) then (Yes)
      while (More logs to process?)
        :Parse Log Data;
        :Find Employee in local DB;
        if (Employee Exists?) then (Yes)
          :Check for Duplicate Log;
          if (Is Duplicate?) then (No)
            :Save Log to DB (in transaction);
          else (Yes)
            :Log "Skipping duplicate";
          endif
        else (No)
          :Log "Unknown Employee ID";
        endif
      endwhile
      :Update Last Sync Timestamp;
      :Commit Transaction;
    else (No)
      :Log "No new logs found";
    endif
  else (No)
    :Log "Device Connection Failed";
    :Send Alert to Admin;
  endif
  :Release Lock;
else (No)
  :Log "Skipping, previous job active";
endif
stop
```

3.3 – Decision Matrix & Escalation Rules
| Decision Point | Condition | Yes → | No → | Owner | Escalation |
|---|---|---|---|---|---|
| Lock Acquired? | lock.acquire(blocking=false) | Continue sync | Skip run, log info | Dev | N/A |
| Connection Successful? | Device responds to ping/SDK | Fetch logs | Log error, send alert | SRE/DevOps | On-call SRE after 3 failures |
| Employee Exists? | Employee.objects.filter(...).exists() | Process log | Log warning, skip | HR/Admin | أسبوعي لمراجعة المعرّفات غير المعروفة |
| Is Duplicate? | AttendanceLog.objects.filter(...).exists() | Skip log | Save new log | Dev | N/A |

3.6 – Mapping to Testing (BDD)
- Scenario: Successful sync with new logs
  - Given آخر مزامنة كانت 10:00
  - And الجهاز يحتوي 3 سجلات جديدة بعد 10:00 لموظفين معروفين
  - When تعمل مهمة المزامنة
  - Then تُضاف 3 سجلات جديدة وتُحدّث خانة آخر مزامنة لأحدث وقت

- Scenario: Sync fails due to device connection error
  - Given الجهاز غير متصل
  - When تعمل مهمة المزامنة
  - Then يتم تسجيل خطأ اتصال وإرسال تنبيه ولا تُضاف سجلات

المراجع
- Phase‑2: `docs/phase-2.md`
- ADR: `docs/adr/0001-choose-architecture.md`