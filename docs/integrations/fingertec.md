# FingerTec Integration (SDK/DB Adapter)

Modes
- SDK: يتطلب ربط SDK الخاص بجهاز FingerTec (سيتم دمجه لاحقاً) — استخدم `FINGERTEC_MODE=sdk` واملأ `FINGERTEC_IP`, `FINGERTEC_PORT`.
- DB: القراءة من قاعدة بيانات Ingress/TCMSv3/… عبر SQLAlchemy/ODBC — استخدم `FINGERTEC_MODE=db`.

Environment Variables (DB mode)
- `FINGERTEC_DB_URL`: رابط الاتصال (مثال MSSQL عبر ODBC):
  - `mssql+pyodbc://USER:PASSWORD@DSN?driver=ODBC+Driver+17+for+SQL+Server`
- إما تحدد استعلاماً جاهزاً:
  - `FINGERTEC_DB_QUERY`: يجب أن يُرجع الأعمدة: `employee_id`, `timestamp`, `type` (اختياري)
- أو تحدد ميتاداتا الجدول:
  - `FINGERTEC_DB_TABLE`: اسم الجدول/العرض
  - `FINGERTEC_DB_COL_EMP`: عمود رقم/معرف الموظف على الجهاز
  - `FINGERTEC_DB_COL_TIME`: عمود وقت التسجيل
  - `FINGERTEC_DB_COL_TYPE`: عمود نوع السجل (اختياري)
- تعيين قيم التعيين لـ IN/OUT (إن لزم):
  - `FINGERTEC_DB_TYPE_IN_VALUES`: افتراضياً `IN,I,0`
  - `FINGERTEC_DB_TYPE_OUT_VALUES`: افتراضياً `OUT,O,1`

Examples (MSSQL Ingress)
- Using metadata:
```
FINGERTEC_MODE=db
FINGERTEC_DB_URL=mssql+pyodbc://user:pass@INGRESS_DSN?driver=ODBC+Driver+17+for+SQL+Server
FINGERTEC_DB_TABLE=att_logs
FINGERTEC_DB_COL_EMP=emp_id
FINGERTEC_DB_COL_TIME=scan_time
FINGERTEC_DB_COL_TYPE=direction
FINGERTEC_DB_TYPE_IN_VALUES=IN,I
FINGERTEC_DB_TYPE_OUT_VALUES=OUT,O
```
- Using raw query:
```
FINGERTEC_DB_QUERY=SELECT emp_id as employee_id, scan_time as timestamp, direction as type FROM att_logs WHERE scan_time > :since ORDER BY scan_time ASC
```

Notes
- يجب أن تُرجع الاستعلامات السجلات الأحدث من `:since` بترتيب زمني تصاعدي.
- يحوّل المهايئ قيم `type` إلى IN/OUT بناءً على اللوائح أعلاه.
- تأكد من وجود تعيين بين معرف الموظف القادم من الجهاز وحقل `employees.employee_id` محلياً.