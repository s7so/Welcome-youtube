### Traceability — US-03 Sync Attendance: Flowchart → Pseudocode

| Flow Step | Module / Function (proposed) | Pseudocode snippet |
|---|---|---|
| Acquire Lock | `attendance.tasks.sync.acquire_job_lock()` | `if not lock.acquire(blocking=False): log.info("Skipping..."); return` |
| Get Last Sync Timestamp | `attendance.services.sync_state.get_last_sync()` | `last_ts = SyncState.get("attendance").last_ts or epoch` |
| Connect to Device | `attendance.integrations.fingertec.connect()` | `conn = FingerTecSDK.connect(ip, port, timeout)` |
| Fetch New Logs | `attendance.integrations.fingertec.fetch_logs_since(last_ts)` | `logs = conn.fetch_logs(since=last_ts)` |
| Parse Log Data | `attendance.integrations.fingertec.parse_log(raw)` | `emp_id, ts, kind = parse(raw)` |
| Find Employee | `employees.repo.get_by_identifier(emp_id)` | `emp = Employee.objects.filter(employee_id=emp_id).first()` |
| Check Duplicate | `attendance.repo.log_exists(emp.id, ts)` | `exists = AttendanceLog.objects.filter(employee=emp, check_time=ts).exists()` |
| Save Log (tx) | `attendance.services.ingest.save_log(emp, ts, kind)` | `with transaction.atomic(): AttendanceLog.create(...)` |
| Update Last Sync | `attendance.services.sync_state.set_last_sync(ts)` | `SyncState.set("attendance", latest_ts)` |
| Release Lock | `attendance.tasks.sync.release_job_lock()` | `lock.release()` |
| Alert on Failure | `platform.alerting.notify_admin(msg)` | `send_email_or_webhook(msg)` |

Draft Python pseudocode
```python
def run_sync_job():
    lock = acquire_job_lock()
    if not lock:
        log.info("Skipping, previous job active")
        return
    try:
        last_ts = get_last_sync()
        conn = connect_to_fingertec()
        if not conn:
            log.error("Device connection failed")
            notify_admin("FingerTec connection failed")
            return
        logs = fetch_logs_since(conn, last_ts)
        if not logs:
            log.info("No new logs found")
            return
        with transaction.atomic():
            latest = last_ts
            for raw in logs:
                emp_id, ts, kind = parse_log(raw)
                emp = find_employee(emp_id)
                if not emp:
                    log.warning("Unknown Employee ID: %s", emp_id)
                    continue
                if log_exists(emp.id, ts):
                    log.info("Skipping duplicate: %s %s", emp_id, ts)
                    continue
                save_log(emp, ts, kind)
                latest = max(latest, ts)
            set_last_sync(latest)
    finally:
        release_job_lock()
```