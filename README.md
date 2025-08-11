# Atlas - نظام إدارة الحضور والانصراف

نظام ويب حديث لإدارة حضور الموظفين والانصراف، مبني باستخدام Django و Django REST Framework.

## الميزات الرئيسية

- **إدارة الموظفين**: إضافة، تعديل، وحذف بيانات الموظفين
- **سجل الحضور**: تتبع دخول وخروج الموظفين
- **التكامل مع أجهزة البصمة**: دعم أجهزة FingerTec
- **التقارير**: تقارير شهرية وإدارية شاملة
- **رفع البيانات المجمع**: استيراد بيانات الموظفين عبر CSV
- **إدارة الصلاحيات**: نظام صلاحيات متقدم (HR Admin, Department Manager, Auditor)

## المتطلبات

- Python 3.12+
- PostgreSQL 16+
- Redis (لـ Celery)
- Docker & Docker Compose (اختياري)

## التثبيت والتشغيل

### باستخدام Docker (موصى به)

```bash
# استنساخ المشروع
git clone <repository-url>
cd atlas

# تشغيل الخدمات
docker compose up -d

# إنشاء مستخدم مدير
docker compose exec web python manage.py createsuperuser

# فتح المتصفح
open http://localhost:8000
```

### التثبيت المحلي

```bash
# إنشاء بيئة افتراضية
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# أو
.venv\Scripts\activate  # Windows

# تثبيت المتطلبات
pip install -r requirements.txt
pip install -r requirements-dev.txt

# إعداد قاعدة البيانات
python manage.py migrate

# إنشاء مستخدم مدير
python manage.py createsuperuser

# تشغيل الخادم
python manage.py runserver
```

## الاختبارات

### تشغيل جميع الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest

# تشغيل الاختبارات مع تفاصيل أكثر
pytest -v

# تشغيل الاختبارات مع تغطية
pytest --cov=apps --cov-report=html
```

### أنواع الاختبارات

#### اختبارات الوحدة (Unit Tests)
```bash
# تشغيل اختبارات الوحدة فقط
pytest -m unit

# تشغيل اختبارات الوحدة مع تفاصيل
pytest -m unit -v
```

#### اختبارات التكامل (Integration Tests)
```bash
# تشغيل اختبارات التكامل فقط
pytest -m integration

# تشغيل اختبارات API
pytest -m api

# تشغيل اختبارات المزامنة
pytest -m sync

# تشغيل اختبارات رفع البيانات المجمع
pytest -m bulk_upload
```

#### اختبارات محددة
```bash
# تشغيل اختبارات ملف معين
pytest tests/test_integration.py

# تشغيل اختبار فئة معينة
pytest tests/test_integration.py::TestEmployeeIntegration

# تشغيل اختبار دالة معينة
pytest tests/test_integration.py::TestEmployeeIntegration::test_employee_list_authorized
```

### تشغيل الاختبارات مع قاعدة بيانات

```bash
# تشغيل الاختبارات مع قاعدة بيانات PostgreSQL
DATABASE_URL=postgresql+psycopg://atlas:atlas@localhost:5432/atlas pytest -m integration

# تشغيل الاختبارات مع قاعدة بيانات SQLite (أسرع للاختبارات)
DATABASE_URL=sqlite:///test.db pytest -m integration
```

## اختبارات Docker

### إعداد بيئة الاختبار

```bash
# إعداد بيئة الاختبار فقط
make setup-test-env

# أو باستخدام السكريبت مباشرة
./scripts/run-tests.sh --setup
```

### تشغيل الاختبارات باستخدام Docker

```bash
# تشغيل جميع الاختبارات
make test-docker

# تشغيل اختبارات الوحدة فقط
make test-docker-unit

# تشغيل اختبارات التكامل فقط
make test-docker-int

# تشغيل اختبارات API
make test-docker-api

# تشغيل اختبارات المزامنة
make test-docker-sync

# تشغيل اختبارات رفع البيانات
make test-docker-bulk

# تشغيل الاختبارات مع تغطية
make test-docker-cov
```

### أوامر Docker المتقدمة

```bash
# تشغيل اختبارات محددة
./scripts/run-tests.sh tests/test_unit.py

# تشغيل اختبارات مطابقة نمط معين
./scripts/run-tests.sh -k 'test_employee'

# تشغيل اختبارات مع تفاصيل أكثر
./scripts/run-tests.sh -v

# تشغيل اختبارات مع تغطية
./scripts/run-tests.sh -c

# إيقاف الحاويات بعد التشغيل
./scripts/run-tests.sh -d

# عرض المساعدة
./scripts/run-tests.sh -h
```

### تنظيف بيئة الاختبار

```bash
# تنظيف ملفات الاختبار
make clean

# تنظيف حاويات Docker
make clean-docker
```

## هيكل المشروع

```
atlas/
├── apps/
│   ├── core/           # الوظائف الأساسية والصلاحيات
│   ├── employees/      # إدارة الموظفين
│   ├── attendance/     # سجل الحضور والمزامنة
│   ├── reports/        # التقارير
│   └── integrations/   # التكامل مع الأجهزة الخارجية
├── atlas/              # إعدادات Django الرئيسية
├── tests/              # الاختبارات
│   ├── test_unit.py           # اختبارات الوحدة
│   ├── test_integration.py    # اختبارات التكامل
│   ├── test_bulk_upload.py    # اختبارات رفع البيانات
│   ├── test_sync_integration.py # اختبارات المزامنة
│   └── test_docker_integration.py # اختبارات بيئة Docker
├── scripts/
│   └── run-tests.sh    # سكريبت تشغيل الاختبارات
├── requirements.txt    # متطلبات الإنتاج
├── requirements-dev.txt # متطلبات التطوير
├── pytest.ini         # إعدادات pytest
├── .flake8            # إعدادات flake8
├── .coveragerc        # إعدادات تغطية الاختبارات
├── docker-compose.test.yml # إعدادات Docker للاختبارات
├── Dockerfile.test     # Dockerfile للاختبارات
├── Makefile           # أوامر مفيدة
└── docker-compose.yml # إعدادات Docker
```

## API Endpoints

### الموظفين
- `GET /api/employees/` - قائمة الموظفين
- `POST /api/employees/` - إضافة موظف جديد
- `GET /api/employees/{id}/` - تفاصيل موظف
- `PATCH /api/employees/{id}/` - تحديث موظف
- `POST /api/employees/bulk-upload/` - رفع بيانات مجمع

### الحضور
- `GET /api/attendance/` - قائمة سجلات الحضور
- `GET /api/attendance/?employee=EMP-001` - فلترة حسب الموظف
- `GET /api/attendance/?log_type=IN` - فلترة حسب نوع السجل

### التقارير
- `GET /api/reports/monthly/?year=2024&month=1` - التقرير الشهري
- `GET /api/reports/department-monthly/?year=2024&month=1` - ملخص الأقسام
- `GET /api/reports/work-hours/?year=2024&month=1` - ساعات العمل

### النظام
- `GET /api/status/` - حالة النظام

## إدارة الصلاحيات

### الأدوار المتاحة
- **HR_Admin**: صلاحيات كاملة على النظام
- **Department_Manager**: صلاحيات محدودة على قسم معين
- **Auditor**: صلاحيات قراءة فقط

### إنشاء المستخدمين والأدوار
```bash
# إنشاء أدوار افتراضية
python manage.py seed_initial_data

# إنشاء مستخدم مع دور HR Admin
python manage.py shell
```
```python
from django.contrib.auth.models import User, Group
from apps.core.auth import ROLE_HR_ADMIN

# إنشاء مستخدم
user = User.objects.create_user('hr_user', 'hr@example.com', 'password123')

# إضافة دور HR Admin
hr_group = Group.objects.get(name=ROLE_HR_ADMIN)
user.groups.add(hr_group)
```

## التطوير

### إضافة اختبارات جديدة

#### اختبارات الوحدة
```python
@pytest.mark.unit
class TestNewFeature:
    def test_new_functionality(self):
        # اختبار الوظيفة الجديدة
        assert True
```

#### اختبارات التكامل
```python
@pytest.mark.integration
@pytest.mark.api
class TestNewAPI:
    def setup_method(self):
        # إعداد البيانات
        pass
    
    def test_new_endpoint(self):
        # اختبار النقطة النهائية الجديدة
        assert True
```

### أوامر Make المفيدة

```bash
# عرض جميع الأوامر المتاحة
make help

# تثبيت متطلبات التطوير
make install-dev

# تشغيل الاختبارات المحلية
make test

# تشغيل الاختبارات مع Docker
make test-docker

# تنظيف ملفات الاختبار
make clean

# فحص الكود
make lint

# فحص Django
make check
```

### تشغيل الاختبارات في CI/CD

```yaml
# .github/workflows/ci.yml
- name: Tests
  run: |
    python manage.py migrate
    pytest -m unit
    pytest -m integration
```

## المساهمة

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف `LICENSE` للتفاصيل.

## الدعم

للأسئلة والدعم التقني، يرجى التواصل مع فريق التطوير.