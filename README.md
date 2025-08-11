### نظام إدارة الحضور والانصراف الحديث — Project Atlas

نظام داخلي لإدارة الحضور والانصراف والإجازات وتقارير الموارد البشرية، مخصص للعمل داخل شبكة الشركة، مع تكامل مع جهاز البصمة (FingerTec).

- المالك/الراعي: شركة مصافي الوسط | قسم تقنية المعلومات والاتصالات
- تاريخ البدء: 24/05/2024
- الإصدار المستهدف (MVP): بعد 3 أشهر من تاريخ البدء (تقدير أولي)
- الحالة الحالية: Phase‑0 مكتملة (مسودة أولية)

روابط وثائق المشروع:
- وثيقة Phase‑0: `docs/phase-0.md`
- وثيقة Phase‑1: `docs/phase-1.md`
- وثيقة Phase‑2: `docs/phase-2.md`
- وثيقة Phase‑3: `docs/phase-3.md`
- سجل القرارات الهندسية (ADR): `docs/adr/0001-choose-architecture.md`
- قالب مفاضلة RICE: `docs/templates/rice-template.csv`
- سجل المخاطر: `docs/risk-register.csv`

مخططات التدفق والربط:
- مخطط المزامنة (US-03): `docs/flowcharts/us-03-sync-attendance.puml` → `docs/flowcharts/us-03-sync-attendance.svg`
- التتبع إلى شبه‑شيفرة: `docs/traceability/flow-to-pseudocode.md`

الخطوة التالية المقترحة:
- الانتقال إلى Phase‑4 (Architecture & Tech Stack) باعتماد Django/DRF وPostgreSQL ووضع التصميم الطبقي للتكامل مع FingerTec.