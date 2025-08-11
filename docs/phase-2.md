### Phase 2 – التفكير بالبيانات (Data Mindset) — Project Atlas

🚀 ملخص سريع
- نموذج البيانات يركز على: الموظفين، الأقسام، سجلات الحضور، الإجازات، والعطل الرسمية.
- مواصفات الإدخال: تعريف دقيق لحقول نموذج الموظف مع قواعد تحقق على مستوى الخادم وقاعدة البيانات.
- الأداء والموثوقية: SLI/SLO واضحة لتقارير الحضور وواجهات CRUD الأساسية.
- الأمان والخصوصية: RBAC، تمييز حقول PII، الالتزام بـ OWASP Top‑10، وتشفير at‑rest للحقول الحساسة.
- القابلية للتوسع: فهرسة مركبة، وخيار التقسيم (Partitioning) لجدول سجلات الحضور عند نمو البيانات.
- النسخ الاحتياطي والاستعادة: نسخ ليلية كاملة + PITR عبر WAL، RTO ≤ 2h، RPO ≤ 15m.
- سياسة الاحتفاظ: محاذاة مع Phase‑0 — سجلات الحضور تحفظ 5 سنوات ثم تُؤرشف.

### 2.0 – Input Specification (نموذج Employee كمثال)

| # | الحقل | النوع | قيود | مثال | Tags |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | full_name | String | مطلوب، ≤ 100 حرف | "علي حسن محمد" | #PII |
| 2 | employee_id | String | مطلوب، فريد، ≤ 20 حرف، [A‑Z0‑9-/_] | "EMP-12345" | #identifier |
| 3 | department_id | UUID | مطلوب، موجود في Departments | "b2a6...-uuid" | #ref |
| 4 | is_active | Boolean | مطلوب، الافتراضي true | true | #status |
| 5 | job_title | String | اختياري، ≤ 100 حرف | "مهندس برمجيات" | #optional |

Validation rules (server):
- التحقق من فريدية `employee_id` قبل الحفظ، مع فهرس/قيد UNIQUE على مستوى قاعدة البيانات.
- التحقق من وجود `department_id` في جدول `departments`.
- قصّ المسافات الزائدة وتطبيع النصوص (normalize) للحقول النصية.
- رفض القيم التي تتجاوز الحدود (مثل طول النص)، وإرجاع رسائل أخطاء واضحة للمستخدم.

### 2.1 – Entity / Data Model (ER)

Entity: Department
- `Department { id UUID PK, name String UNIQUE, created_at Timestamptz }`

Entity: Employee
- `Employee { id UUID PK, employee_id String UNIQUE #identifier, full_name String #PII, job_title String?, department_id UUID FK -> Department.id, is_active Boolean DEFAULT true, created_at Timestamptz }`

Entity: AttendanceLog
- `AttendanceLog { id BIGSERIAL PK, employee_id UUID FK -> Employee.id, check_time Timestamptz, log_type Enum("IN","OUT"), source String?, created_at Timestamptz }`

Entity: LeaveType (لاحقاً)
- `LeaveType { id UUID PK, name String UNIQUE }`

Entity: LeaveRequest (لاحقاً)
- `LeaveRequest { id UUID PK, employee_id UUID FK -> Employee.id, start_date Date, end_date Date, leave_type_id UUID FK -> LeaveType.id, status Enum("PENDING","APPROVED","REJECTED"), created_at Timestamptz }`

Entity: OfficialHoliday (لاحقاً)
- `OfficialHoliday { id UUID PK, name String, holiday_date Date UNIQUE }`

ملاحظات خصوصية:
- `full_name` وحقول تعريف أخرى هي PII. يجب ضبط سياسات وصول وأذونات دقيقة، وتفعيل التتبع (Audit Log) لعمليات القراءة الحساسة إذا لزم.

### 2.2 – Relationships
- Department → Employee: One‑to‑Many
- Employee → AttendanceLog: One‑to‑Many
- Employee → LeaveRequest: One‑to‑Many (لاحقاً)
- LeaveRequest → LeaveType: Many‑to‑One (لاحقاً)

### 2.3 – SQL Schema Example (PostgreSQL)

```sql
-- تمكين امتداد UUID (إن لم يكن مفعّلاً) و/أو توليد UUID عبر التطبيق
-- CREATE EXTENSION IF NOT EXISTS pgcrypto; -- لاستخدام gen_random_uuid()

-- الأقسام
CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- الموظفون
CREATE TABLE employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  job_title TEXT,
  department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- نوع السجل (اختياري: ENUM)
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'attendance_log_type') THEN
    CREATE TYPE attendance_log_type AS ENUM ('IN','OUT');
  END IF;
END $$;

-- سجلات الحضور
CREATE TABLE attendance_logs (
  id BIGSERIAL PRIMARY KEY,
  employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  check_time TIMESTAMPTZ NOT NULL,
  log_type attendance_log_type NOT NULL,
  source TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- فهارس لتحسين أداء التقارير
CREATE INDEX idx_attendance_employee_time ON attendance_logs(employee_id, check_time DESC);
CREATE INDEX idx_attendance_time ON attendance_logs(check_time DESC);

-- (اختياري لاحقاً) التقسيم حسب الشهر عند تضخم البيانات:
-- CREATE TABLE attendance_logs_2025_01 PARTITION OF attendance_logs
--   FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

Indexing notes:
- الفهرس المركّب `(employee_id, check_time DESC)` حيوي لتقارير الموظف وحسابات الساعات.
- فهرس على `check_time` فقط يفيد استعلامات أحدث السجلات عامةً.
- يمكن تفعيل Partitioning حسب الشهر إذا تجاوز عدد السجلات 10+ مليون سجل.

### 2.4 – Non‑Functional Requirements (NFR)

| الفئة | المتطلب | مقياس | ملاحظة |
| :--- | :--- | :--- | :--- |
| الأداء | توليد تقرير شهري لقسم (≈50 موظف) | ≤ 5 ثوانٍ (p95) | في ظل الاستخدام العادي |
| التوسّع | التعامل مع 1000 موظف و5 سنوات سجلات | ≈ 2M+ سجل | يتطلب فهرسة قوية وربما Partitioning |
| الاتساق | سحب البيانات من FingerTec | معاملات ACID | عملية السحب داخل Transaction |
| الأمان | التحكم بالوصول للبيانات | RBAC + مداها بالأقسام | مدير القسم يرى قسمه فقط |

### 2.5 – SLI / SLO (APIs الحرجة)
- GET `/api/reports/monthly`:
  - التوفر (SLO، 30 يوم): 99.5% خلال ساعات العمل الرسمية.
  - الكمون (Latency p95): ≤ 5000 ms.
- GET `/api/employees`:
  - التوفر: 99.9%.
  - الكمون p95: ≤ 200 ms.
- POST `/api/employees`:
  - الكمون p95: ≤ 200 ms.

### 2.6 – Monitoring & Alerts
- قاعدة البيانات: رصد الاستعلامات البطيئة > 500 ms، ولوحة Grafana لعرضها.
- أخطاء الخادم (5xx): تنبيه عند > 1% لمدة 5 دقائق.
- تكامل FingerTec: تنبيه فوري عند فشل محاولتي سحب متتاليتين.
- مؤشرات تتبع: عدد السجلات المسحوبة يومياً، زمن آخر مزامنة ناجحة.

### 2.7 – Caching Strategy
- Cache: `GET /api/departments` و`GET /api/leave-types` (TTL: 1 ساعة) لأنها نادراً ما تتغير.
- No-Cache مبدئياً للتقارير الشهرية لضمان الدقة؛ يمكن دراسة تخزين مؤقت للنتائج المعقّدة بوسيط قصير لاحقاً.

### 2.8 – Backup & Restore / DR
- Backup: نسخة احتياطية كاملة يومية لقاعدة PostgreSQL + تفعيل WAL Archiving (PITR).
- RTO: ≤ 2 ساعات.
- RPO: ≤ 15 دقيقة.
- Restore Test: اختبار استعادة ربع سنوي للتحقق من صحة النسخ الاحتياطية والإجراءات.

### 2.9 – Data Retention & Archiving
- محاذاة مع Phase‑0:
  - سجلات الحضور: تُحفظ 5 سنوات في القاعدة التشغيلية.
  - بعد 5 سنوات: أرشفة إلى تخزين أرخص (CSV/Parquet) والاحتفاظ وفق سياسة الشركة.
  - بيانات الموظفين غير النشطين: تُؤرشف بعد سنة من المغادرة وتحذف بعد 5 سنوات.

### 2.10 – Privacy & Compliance
- تصنيف البيانات: `full_name`، معرفات الموظف، بيانات الحضور تعتبر PII.
- الوصول: تقييد صارم حسب الدور والقسم. تسجيل عمليات الوصول الحساسة عند الحاجة.
- التشفير: HTTPS داخل الشبكة (in‑transit) وتشفير الحقول الحساسة at‑rest.

### 2.11 – Access Control & Security
- RBAC: أدوار مثل HR Admin، Department Manager، Read‑only Auditor.
- نطاق الوصول: مدراء الأقسام يرون بيانات أقسامهم فقط (سياسة API + استعلامات مقيّدة).
- ORM: استخدام Django ORM/DRF لحماية من SQL Injection.
- أسرار النظام: إدارة عبر Secrets Manager/بيئة، وعدم تخزينها في المستودع.
- OWASP Top‑10: اعتمادها كـ Acceptance Gate للـ Web/API.
- Audit Logs: تسجيل تغييرات CRUD على كيانات PII الأساسية.

### 2.12 – Migration Strategy
- استخدام نظام الترحيـلات المدمج (Django Migrations).
- جميع تغييرات المخطط تتم عبر ملفات Migration خاضعة للمراجعة.
- خطة تراجع (Rollback): لقطة قاعدة بيانات قبل ترحيلات ضخمة؛ واستخدام معاملات عند الترحيل.

### 2.13 – Data Quality & Observability
- مهمة دورية لاكتشاف سجلات حضور يتيمة (لا مرجع `employee_id`).
- تتبع يومي لعدد السجلات المستوردة؛ تنبيه عند انحرافات كبيرة.
- فحوص اتساق: عدم السماح بـ `end_date < start_date` في الإجازات؛ ضمان تسلسل منطقي لسجلات IN/OUT في التقارير.

### 2.16 – Definition of Ready (DoR) — Phase‑2
- [✅] الحقول الأساسية والجداول محددة.
- [✅] مخطط ER واضح وروابط الكيانات موثقة.
- [✅] SLOs أولية للـ APIs الحرجة.
- [✅] خطة احتفاظ بالبيانات والنسخ الاحتياطي والاستعادة موثقة.
- [✅] اعتبارات الأمان والخصوصية مدمجة.

اقتراح استراتيجي
- اعتماد Django كإطار عمل أساسي:
  - يوفر RBAC مدمجاً ولوحة Admin قوية وMigrations جاهزة.
  - ORM ناضج وأمان افتراضي جيد ضد هجمات شائعة.
  - يسمح بالتركيز على منطق الأعمال (التكامل والتقارير) بدلاً من البنية التحتية الأساسية.