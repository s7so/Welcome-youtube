### Phase 5 – Architecture & Tech Stack — Project Atlas

🎯 الهدف
تثبيت المكدس التقني والمعمارية التشغيلية لتطبيق الويب الداخلي لإدارة الحضور، مع تحديد البنية الطبقية، المكونات، وطرق النشر والمراقبة.

5.0 – Tech Choices (MVP)
- Backend: Django 5.x + Django REST Framework
- Background jobs: Celery 5.x
- Broker/Cache: Redis 7.x
- Database: PostgreSQL 16.x
- Web server: Gunicorn (workers uvicorn/ASGI)
- Reverse proxy: Nginx (داخل الشبكة)
- Auth: LDAP/AD لاحقاً أو نظام مستخدمين داخلي كبداية
- Containerization: Docker (Compose) للنشر الداخلي
- OS target: Linux (on‑prem)

5.1 – High‑level Architecture
- Web/API Service (Django + DRF): يقدم واجهات CRUD والتقارير.
- Worker Service (Celery): ينفذ مزامنة الحضور ومهام الدُفعات.
- PostgreSQL: تخزين دائم للبيانات التشغيلية.
- Redis: وسيط Celery + Cache بسيط.
- FingerTec Integration: طبقة تكامل للوصول إلى الجهاز/قاعدة Ingress.
- Observability: Logging موحد + تنبيهات فشل التكامل.

Data Flow (US‑03)
- Scheduler → Celery Task → Acquire Lock (Redis) → Connect FingerTec → Fetch Logs → Validate/De‑dup → Store in Postgres → Update sync state → Log/Alert.

5.2 – Project Structure (proposed)
```
atlas/                      # جذر مشروع Django
  manage.py
  atlas/                    # إعدادات المشروع (settings/asgi/urls)
  apps/
    core/
    employees/
    attendance/
    reports/
    integrations/fingertec/
    platform/alerting/
  tests/
  requirements.txt
```
- `apps/attendance/tasks/sync.py`: يحتوي `run_sync_job` وفق Phase‑4.
- `apps/integrations/fingertec/`: واجهة SDK/DB adapter لعزل مزوّد البصمة.

5.3 – Configuration & Environments
- Envs: `development`, `staging`, `production`.
- Secrets via env vars: `DJANGO_SECRET_KEY`, `DATABASE_URL` أو (DB_*), `REDIS_URL`, `FINGERTEC_IP`, `FINGERTEC_PORT`, `SYNC_INTERVAL_MINUTES`.
- Logging: JSON logs في الإنتاج؛ مستوى INFO افتراضياً.

5.4 – Dependencies (pinning)
- انظر `requirements.txt`:
  - Django, djangorestframework, psycopg[binary], celery, redis, python‑dotenv, gunicorn, uvicorn[standard].

5.5 – Deployment (on‑prem, Docker Compose)
- Services: web, worker, redis, postgres, nginx (اختياري).
- Volumes: `pg_data` لقاعدة البيانات؛ لا تُخزن الأسرار في الصور.
- Healthchecks: web on `/_healthz`, db via pg_isready, redis PING.

5.6 – Observability
- Logs: هيكل موحد يحتوي `job_id`, `last_sync_ts`, `records_fetched`, `records_saved`.
- Alerts: فشل اتصال FingerTec مرتين متتاليتين ⇒ تنبيه.
- Slow queries: تنبيه > 500ms على استعلامات التقارير.

5.7 – Security
- HTTPS داخلي بين Nginx والعميل؛ شبكات داخلية لخدمات Compose.
- RBAC بالتوافق مع الأدوار المحددة.
- OWASP Top‑10: XSS, CSRF, SQLi, AuthZ كمعايير قبول.
- Backups: ليلية + PITR؛ اختبار استعادة ربع سنوي.

5.8 – Risks & Mitigations (Tech)
- FingerTec SDK/DB variance: عزل عبر adapter؛ دعم fallback لقراءة DB Ingress read‑only.
- تضخم سجلات الحضور: فهارس مركبة + partitioning حسب الشهر عند >10M سجل.
- مهام متزامنة: قفل Redis بأسماء jobs، ومقاييس لمنع التداخل.

5.9 – Definition of Ready (DoR) — Phase‑5
- [✅] المكدس التقني محدد ومقبول (Django/DRF, Celery, Postgres, Redis).
- [✅] الهيكل العام للمشروع واضح.
- [✅] إعدادات البيئة والمتغيرات موثقة.
- [✅] استراتيجية النشر والنسخ الاحتياطي موثقة.
- [✅] اعتبارات الأمان والمراقبة محددة.

المراجع
- Phase‑2: `docs/phase-2.md`
- Phase‑3: `docs/phase-3.md`
- Pseudo‑code: `docs/pseudocode/sync_attendance_logs.md`