### Error and Alert Messages — Attendance Sync

- "Sync job is already running. Skipping this run.":
  - Cause: Lock not acquired (another job in progress).
  - Action: None. Informational.

- "Failed to connect to FingerTec device.":
  - Cause: Device offline/unreachable.
  - Alert: Critical — notify SRE/Admin.

- "No new attendance logs found.":
  - Cause: No logs since last sync timestamp.
  - Action: None.

- "Skipping log for unknown employee ID: {id}":
  - Cause: Employee identifier not found locally.
  - Action: Weekly review by Admin/HR.

- "Skipping duplicate log for employee {id} at {timestamp}":
  - Cause: Duplicate record detected.
  - Action: None.

- "Attendance sync job failed unexpectedly!":
  - Cause: Unhandled exception.
  - Alert: Critical — notify SRE/Admin.