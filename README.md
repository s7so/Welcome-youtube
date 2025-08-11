# Atlas - نظام إدارة الحضور والانصراف

نظام ويب حديث لإدارة حضور الموظفين والانصراف، مبني باستخدام Django و Django REST Framework مع واجهة مستخدم مذهلة.

## 🌟 المميزات الرئيسية

- **واجهة مستخدم مذهلة**: تصميم عصري مع تأثيرات زجاجية وتدرجات لونية
- **إدارة الموظفين**: إضافة، تعديل، وحذف بيانات الموظفين
- **سجل الحضور**: تتبع دخول وخروج الموظفين
- **التكامل مع أجهزة البصمة**: دعم أجهزة FingerTec
- **التقارير**: تقارير شهرية وإدارية شاملة مع رسوم بيانية تفاعلية
- **رفع البيانات المجمع**: استيراد بيانات الموظفين عبر CSV
- **إدارة الصلاحيات**: نظام صلاحيات متقدم (HR Admin, Department Manager, Auditor)
- **الوضع المظلم**: دعم كامل للوضع المظلم مع حفظ التفضيلات

## 🎨 التقنيات المستخدمة

### **Backend:**
- Django 5.0.6
- Django REST Framework
- PostgreSQL
- Redis (لـ Celery)
- Celery (للمهام الخلفية)

### **Frontend:**
- Tailwind CSS (تصميم سريع وجميل)
- Alpine.js (تفاعلات خفيفة وسريعة)
- Chart.js (رسوم بيانية تفاعلية)
- Heroicons (أيقونات جميلة)
- Cairo Font (خط عربي جميل)

## 📋 المتطلبات

- Python 3.12+
- Node.js 18+ (للواجهة الأمامية)
- PostgreSQL 16+
- Redis (لـ Celery)
- Docker & Docker Compose (اختياري)

## 🚀 التثبيت والتشغيل

### **التثبيت الكامل (موصى به)**

```bash
# استنساخ المشروع
git clone <repository-url>
cd atlas

# إعداد البيئة الكاملة
make setup-full

# تشغيل الخادم
make dev
```

### **التثبيت باستخدام Docker**

```bash
# استنساخ المشروع
git clone <repository-url>
cd atlas

# تشغيل الخدمات
make docker-up

# إنشاء مستخدم مدير
docker compose exec web python manage.py createsuperuser

# فتح المتصفح
open http://localhost:8000
```

### **التثبيت المحلي (خطوة بخطوة)**

#### **1. إعداد Backend:**
```bash
# إنشاء بيئة افتراضية
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# أو
.venv\Scripts\activate  # Windows

# تثبيت المتطلبات
make install-all

# إعداد قاعدة البيانات
make migrate

# إنشاء مستخدم مدير
python manage.py createsuperuser
```

#### **2. إعداد Frontend:**
```bash
# تثبيت تبعيات Node.js
make frontend

# بناء ملفات CSS
make frontend-build

# أو للتطوير مع المراقبة
make frontend-watch
```

#### **3. تشغيل الخادم:**
```bash
# تشغيل الخادم العادي
make dev

# أو تشغيل مع مراقبة Frontend
make dev-with-frontend
```

## 🎨 الواجهة الأمامية

### **المميزات البصرية:**
- **تصميم زجاجي (Glassmorphism)**: بطاقات شفافة مع تأثيرات blur
- **تدرجات لونية مذهلة**: ألوان متعددة مع تأثيرات hover
- **حركات سلسة**: انتقالات وحركات متقدمة
- **الوضع المظلم**: تبديل سلس مع حفظ التفضيلات
- **تصميم متجاوب**: يعمل على جميع الأجهزة

### **أوامر Frontend:**
```bash
# تثبيت التبعيات
make frontend

# بناء للإنتاج
make frontend-build

# التطوير مع المراقبة
make frontend-watch

# تنظيف ملفات البناء
make frontend-clean
```

### **هيكل Frontend:**
```
static/
├── css/
│   ├── tailwind.css          # ملف CSS الرئيسي
│   └── output.css            # ملف CSS المُجمّع
├── js/
│   └── app.js               # JavaScript الرئيسي
└── images/
    └── favicon.ico          # أيقونة الموقع

templates/
├── base.html               # القالب الأساسي
├── dashboard.html          # لوحة التحكم
└── employees/
    └── employee_list.html  # صفحة إدارة الموظفين
```

## 🧪 الاختبارات

### **تشغيل جميع الاختبارات**

```bash
# تشغيل جميع الاختبارات
make test

# تشغيل الاختبارات مع تفاصيل أكثر
pytest -v

# تشغيل الاختبارات مع تغطية
make test-coverage
```

### **أنواع الاختبارات**

#### اختبارات الوحدة (Unit Tests)
```bash
# تشغيل اختبارات الوحدة فقط
make test-unit

# تشغيل اختبارات الوحدة مع تفاصيل
pytest -m unit -v
```

#### اختبارات التكامل (Integration Tests)
```bash
# تشغيل اختبارات التكامل فقط
make test-integration

# تشغيل اختبارات API
make test-api

# تشغيل اختبارات المزامنة
make test-sync

# تشغيل اختبارات رفع البيانات المجمع
make test-bulk
```

### **اختبارات Docker**

```bash
# تشغيل جميع الاختبارات
make test-docker

# تشغيل اختبارات الوحدة فقط
make test-docker-unit

# تشغيل اختبارات التكامل فقط
make test-docker-int

# تشغيل الاختبارات مع تغطية
make test-docker-cov
```

## 📊 API Endpoints

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

## 🎯 إدارة الصلاحيات

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

## 🛠️ التطوير

### **أوامر Make المفيدة**

```bash
# عرض جميع الأوامر المتاحة
make help

# إعداد البيئة الكاملة
make setup-full

# إعداد Frontend فقط
make setup-frontend

# تشغيل الخادم
make dev

# تشغيل مع Frontend watching
make dev-with-frontend

# فحص حالة النظام
make status

# تنظيف الملفات
make clean

# فحص الكود
make lint

# فحص Django
make check
```

### **إضافة اختبارات جديدة**

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

### **تطوير Frontend**

#### إضافة مكونات Alpine.js جديدة:
```javascript
Alpine.data('newComponent', () => ({
    data: [],
    loading: false,
    
    async loadData() {
        this.loading = true;
        // تحميل البيانات
        this.loading = false;
    }
}));
```

#### إضافة أنماط CSS مخصصة:
```css
@layer components {
    .custom-component {
        @apply glass-card p-6 transition-all duration-300;
    }
}
```

## 🚀 النشر

### **إعداد الإنتاج**

```bash
# إعداد البيئة للإنتاج
make deploy-prepare

# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# تشغيل الترحيلات
python manage.py migrate
```

### **تشغيل الاختبارات في CI/CD**

```yaml
# .github/workflows/ci.yml
- name: Backend Tests
  run: |
    make test-unit
    make test-integration

- name: Frontend Build
  run: |
    make frontend-build

- name: Frontend Tests
  run: |
    npm run lint
```

## 📁 هيكل المشروع

```
atlas/
├── apps/
│   ├── core/           # الوظائف الأساسية والصلاحيات
│   ├── employees/      # إدارة الموظفين
│   ├── attendance/     # سجل الحضور والمزامنة
│   ├── reports/        # التقارير
│   └── integrations/   # التكامل مع الأجهزة الخارجية
├── atlas/              # إعدادات Django الرئيسية
├── templates/          # قوالب HTML
│   ├── base.html              # القالب الأساسي
│   ├── dashboard.html         # لوحة التحكم
│   └── employees/
│       └── employee_list.html # إدارة الموظفين
├── static/             # الملفات الثابتة
│   ├── css/
│   │   ├── tailwind.css       # ملف CSS الرئيسي
│   │   └── output.css         # ملف CSS المُجمّع
│   ├── js/
│   │   └── app.js            # JavaScript الرئيسي
│   └── images/
│       └── favicon.ico       # أيقونة الموقع
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
├── package.json        # تبعيات Frontend
├── tailwind.config.js  # إعدادات Tailwind CSS
├── postcss.config.js   # إعدادات PostCSS
├── pytest.ini         # إعدادات pytest
├── .flake8            # إعدادات flake8
├── .coveragerc        # إعدادات تغطية الاختبارات
├── docker-compose.test.yml # إعدادات Docker للاختبارات
├── Dockerfile.test     # Dockerfile للاختبارات
├── Makefile           # أوامر مفيدة
├── FRONTEND.md        # توثيق الواجهة الأمامية
└── docker-compose.yml # إعدادات Docker
```

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

### **معايير المساهمة:**
- اتبع معايير التصميم المحددة
- استخدم الألوان والطبقات المخصصة
- تأكد من التصميم المتجاوب
- اختبر على متصفحات متعددة
- اتبع أفضل ممارسات الأداء

## 📚 التوثيق الإضافي

- [Frontend Documentation](FRONTEND.md) - دليل شامل للواجهة الأمامية
- [API Documentation](docs/api.md) - توثيق API
- [Deployment Guide](docs/deployment.md) - دليل النشر

## 📞 الدعم

للأسئلة والدعم التقني، يرجى التواصل مع فريق التطوير.

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف `LICENSE` للتفاصيل.

---

**تم تطوير هذا النظام بكل حب ❤️ لضمان تجربة مستخدم مذهلة!**