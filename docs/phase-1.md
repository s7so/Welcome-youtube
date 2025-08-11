### Phase 1 – Idea Autopsy (Project Atlas)

1.0 - Vision (1‑sentence)
"تطبيق ويب يساعد الشركة على معرفة حضور الموظفين وإجازاتهم بسهولة، ويُخرج تقارير شهرية دقيقة بضغطة زر."

1.1 - One‑pager / Pitch
- Problem: النظام الحالي قديم، بطيء، صعب الصيانة، ويتطلب تثبيته على أجهزة المستخدمين، مما يعيق الكفاءة والتطوير.
- Solution: بناء تطبيق ويب مركزي وحديث (باستخدام Python/Django أو Flask)، سهل الوصول عبر المتصفح، يوفر واجهة مستخدم نظيفة وتقارير فورية ودقيقة.
- Key metrics: تقليل وقت إعداد التقارير الشهرية بنسبة 50%، نسبة استخدام 95% من قبل المستخدمين المستهدفين، تحميل أي تقرير في أقل من 5 ثوانٍ.
- MVP scope (Top 3 features):
  1) إدارة بيانات الموظفين (إضافة/تعديل).
  2) سحب بيانات الحضور تلقائياً من جهاز البصمة (FingerTec).
  3) توليد تقرير الحضور الشهري الشامل (مع فلترة وطباعة).
- Risks & Assumptions: الخطر الأكبر هو وجود صعوبات تقنية في التكامل مع جهاز البصمة FingerTec. الافتراض الأساسي هو توفر SDK أو طريقة للوصول لقاعدة بيانات الجهاز.
- Stakeholders & approvers: المالك (PO): رئيس قسم تقنية المعلومات/ممثل موارد بشرية. الموافقون الرئيسيون: Tech Lead (AI) ومالك المنتج (PO).

1.2 - Interface Sketch (الوصف المبدئي)
- الرابط: `docs/sketches/01-dashboard.png` (سيتم إنشاؤه لاحقاً).
- الوصف:
  - شريط علوي (Header): شعار "شركة مصافي الوسط" على اليمين، واسم المستخدم المسجل حالياً وزر تسجيل الخروج على اليسار.
  - قائمة تنقل جانبية (Sidebar) على اليمين:
    - الرئيسية (لوحة التحكم)
    - الموظفين
    - التقارير
    - الإعدادات (للمدير فقط)
  - المحتوى الرئيسي (Main Content Area) في صفحة "الرئيسية":
    - بطاقة "إجمالي الموظفين المسجلين".
    - بطاقة "عدد الحاضرين اليوم".
    - بطاقة "آخر عملية سحب بيانات من جهاز البصمة" (مع التاريخ والوقت).

1.3 - Component Inventory
| id | Component | Type | Purpose | State (Design/Dev) |
|---|---|---|---|---|
| C-01 | Sidebar Navigation | Navigation | للتنقل بين أقسام النظام الرئيسية | Concept |
| C-02 | Summary Card | Display | عرض إحصائيات سريعة في لوحة التحكم | Concept |
| C-03 | Data Table | Display | عرض قائمة الموظفين أو سجلات الحضور | Concept |
| C-04 | Primary Button | Button | تنفيذ إجراءات أساسية (مثل "إضافة موظف"، "حفظ") | Concept |
| C-05 | Date Picker | Input | اختيار تاريخ أو نطاق زمني للتقارير | Concept |
| C-06 | Modal Window | Container | نافذة منبثقة لإضافة/تعديل البيانات دون مغادرة الصفحة | Concept |
| C-07 | Search Input | Input | البحث داخل الجداول (مثلاً: البحث عن موظف) | Concept |

1.4 - Interaction Matrix
| Component | Action | Expected Result | Error states | Owner |
|---|---|---|---|---|
| C-04 (Primary Button "إضافة موظف") | Click | تفتح C-06 (Modal Window) مع نموذج فارغ لإضافة موظف. | لا يوجد (الزر دائماً فعال إذا كان للمستخدم صلاحية). | Dev |
| C-03 (Data Table - أيقونة تعديل) | Click | تفتح C-06 (Modal Window) مع ملء حقول النموذج ببيانات الموظف المحدد. | لا يوجد. | Dev |
| C-05 (Date Picker في صفحة التقارير) | Select Date Range | يتم تحديث بيانات التقرير في C-03 (Data Table) لتعكس الفترة الزمنية الجديدة. | رسالة خطأ إذا كان تاريخ النهاية قبل تاريخ البداية. | Dev/QA |
| C-07 (Search Input فوق جدول الموظفين) | Type Text | يتم فلترة الصفوف في C-03 (Data Table) بشكل فوري لإظهار النتائج المطابقة. | "لا توجد نتائج" تظهر إذا لم يتم العثور على موظف. | Dev |

1.5 - Accessibility & Internationalization (a11y / i18n)
- RTL support: نعم، النظام باللغة العربية، دعم RTL شرط أساسي.
- Contrast ratios: لم يتم التحقق بعد؛ شرط قبول لأي مهمة واجهة.
- aria‑labels للحقول: غير موجودة حالياً؛ تُضاف كشرط قبول لضمان سهولة الوصول.

1.6 - Acceptance Criteria (Gherkin Template)
Feature: Employee Management
Scenario: Add a new employee successfully
Given I am a logged-in HR user on the "Employees" page
When I click the "Add Employee" button, fill in a unique employee ID, name, and department, and click "Save"
Then the new employee appears in the data table and a success message is shown.

1.7 - Traceability (linking)
- عند إنشاء المستودع، سيتم إنشاء Issue لكل User Story.
- مثال: قصة "إضافة موظف" ستُربط بـ Issue #1، ويُشار إلى C-04 و C-06 داخل الـ Issue.

1.8 - Prioritization (RICE for MVP features)
| Feature | Reach (R) | Impact (I) | Confidence (C) | Effort (E) | RICE Score |
|---|---:|---:|---:|---:|---:|
| سحب بيانات البصمة (E-03) | 100 | 3 | 70% | 3 | 70 |
| توليد التقارير (E-06) | 10 | 3 | 90% | 3 | 9 |
| إدارة الموظفين (E-02) | 5 | 3 | 100% | 2 | 7.5 |
- القرار: أولوية قصوى لضمان القدرة على سحب البيانات من جهاز البصمة لكونه الأعلى تأثيراً والأكثر خطورة.

1.9 - Security / Privacy notes
- ميزة إدارة الموظفين (E-02) تتعامل مع بيانات تعريف شخصية (PII). يُضاف وسم #PII لجميع Issues المتعلقة.
- التأكد من أن صلاحيات تعديل/حذف الموظفين مقتصرة على الأدوار المخولة (مثل مدير الموارد البشرية).

1.10 - Time‑Box
- 45 دقيقة للرؤية والتصميم، 30 دقيقة للمكونات والتفاعلات. قابل للإنجاز في جلسة واحدة مركزة.

1.11 - Definition of Ready (DoR) — Phase‑1
- [✅] Vision مكتوبة.
- [✅] Sketch موصوف وجاهز للتصميم.
- [✅] Component inventory مبدئي.
- [✅] Top‑3 features مُصنّفة بالأولوية (RICE).
- [✅] تعليم المخاطر الأمنية/الخصوصية.

المراجع
- Phase‑0: `docs/phase-0.md`
- ADR المعمارية: `docs/adr/0001-choose-architecture.md`