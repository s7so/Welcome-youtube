### ADR 0002: اختيار المكدس التقني — Django/DRF + Celery + Postgres + Redis

Status: Accepted
Date: 2025-08-11

Context
- نحتاج إلى تطبيق ويب داخلي مع مهام خلفية موثوقة وتخزين علائقي قوي.
- تكامل مع FingerTec يتطلب عمليات مجدولة ومعاملات سليمة.

Decision
- Backend: Django + DRF
- Jobs: Celery مع Redis كوسيط
- DB: PostgreSQL
- Runtime: Docker/Compose للنشر الداخلي
- Web: Gunicorn (uvicorn workers) خلف Nginx

Consequences
- إيجابي: بيئة Python ناضجة، أدوات إدارة وصلاحيات جاهزة، معاملات ACID، مهام خلفية مستقرة.
- سلبي: يتطلب إدارة Redis وPostgres داخلياً؛ يلزم متابعة الأداء.

Notes
- يمكن إضافة LDAP/AD لاحقاً للمصادقة.
- Partitioning لجدول `attendance_logs` عند زيادة الحجم.