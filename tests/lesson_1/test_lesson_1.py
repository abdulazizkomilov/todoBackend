"""
1-dars — Loyihani sozlash
Tekshiriladi:
  1-qism: Loyiha fayl tuzilmasi (manage.py, core/, tests/)
  2-qism: requirements.txt va o'rnatilgan paketlar
  3-qism: todos app, INSTALLED_APPS, ALLOWED_HOSTS, migration
"""
from pathlib import Path

import django
import pytest
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Template core/ ishlatadi, ba'zi muhitlar config/ ishlatishi mumkin
DJANGO_APP_DIR = (
    BASE_DIR / 'core' if (BASE_DIR / 'core').is_dir()
    else BASE_DIR / 'config'
)


# ── 1-qism: Loyiha fayl tuzilmasi ─────────────────────────────────────────

class TestProjectStructure:
    def test_manage_py_exists(self):
        assert (BASE_DIR / 'manage.py').exists(), (
            "manage.py topilmadi. Loyiha to'g'ri clone qilinganmi?"
        )

    def test_django_project_folder_exists(self):
        assert DJANGO_APP_DIR.is_dir(), (
            "core/ papkasi topilmadi. Repo to'g'ri fork va clone qilinganmi?"
        )

    def test_settings_py_exists(self):
        assert (DJANGO_APP_DIR / 'settings.py').exists(), (
            f"{DJANGO_APP_DIR.name}/settings.py topilmadi."
        )

    def test_urls_py_exists(self):
        assert (DJANGO_APP_DIR / 'urls.py').exists(), (
            f"{DJANGO_APP_DIR.name}/urls.py topilmadi."
        )

    def test_wsgi_py_exists(self):
        assert (DJANGO_APP_DIR / 'wsgi.py').exists(), (
            f"{DJANGO_APP_DIR.name}/wsgi.py topilmadi."
        )

    def test_pytest_ini_exists(self):
        assert (BASE_DIR / 'pytest.ini').exists(), (
            "pytest.ini topilmadi."
        )

    def test_requirements_txt_exists(self):
        assert (BASE_DIR / 'requirements.txt').exists(), (
            "requirements.txt topilmadi."
        )

    def test_tests_folder_exists(self):
        assert (BASE_DIR / 'tests').is_dir(), (
            "tests/ papkasi topilmadi."
        )


# ── 2-qism: requirements.txt va o'rnatilgan paketlar ──────────────────────

class TestRequirements:
    def test_requirements_not_empty(self):
        content = (BASE_DIR / 'requirements.txt').read_text()
        assert content.strip(), "requirements.txt bo'sh."

    def test_django_importable(self):
        try:
            import django  # noqa: F401
        except ImportError:
            pytest.fail(
                "django o'rnatilmagan. "
                "Avval venv ni aktivlashtiring: source venv/bin/activate\n"
                "Keyin: pip install -r requirements.txt"
            )

    def test_rest_framework_importable(self):
        try:
            import rest_framework  # noqa: F401
        except ImportError:
            pytest.fail(
                "djangorestframework o'rnatilmagan. "
                "pip install -r requirements.txt ni bajaring."
            )

    def test_corsheaders_importable(self):
        try:
            import corsheaders  # noqa: F401
        except ImportError:
            pytest.fail(
                "django-cors-headers o'rnatilmagan. "
                "pip install -r requirements.txt ni bajaring."
            )

    def test_pytest_django_importable(self):
        try:
            import pytest_django  # noqa: F401
        except ImportError:
            pytest.fail(
                "pytest-django o'rnatilmagan. "
                "pip install -r requirements.txt ni bajaring."
            )

    def test_django_version_5_or_higher(self):
        major = int(django.__version__.split('.')[0])
        assert major >= 5, (
            f"Django 5+ kerak, hozir: {django.__version__}"
        )


# ── 3-qism: todos app, INSTALLED_APPS, ALLOWED_HOSTS, migration ───────────

class TestTodosApp:
    def test_todos_folder_exists(self):
        assert (BASE_DIR / 'todos').is_dir(), (
            "todos/ papkasi topilmadi. "
            "Quyidagi buyruqni bajaring: python manage.py startapp todos"
        )

    def test_todos_models_py_exists(self):
        assert (BASE_DIR / 'todos' / 'models.py').exists(), (
            "todos/models.py topilmadi. "
            "python manage.py startapp todos to'liq bajariladimi?"
        )

    def test_todos_views_py_exists(self):
        assert (BASE_DIR / 'todos' / 'views.py').exists(), (
            "todos/views.py topilmadi."
        )

    def test_todos_migrations_folder_exists(self):
        assert (BASE_DIR / 'todos' / 'migrations').is_dir(), (
            "todos/migrations/ papkasi topilmadi. "
            "python manage.py startapp todos buyrug'ini bajaring."
        )

    def test_todos_in_installed_apps(self):
        assert 'todos' in settings.INSTALLED_APPS, (
            "'todos' INSTALLED_APPS da yo'q.\n"
            f"{DJANGO_APP_DIR.name}/settings.py faylida INSTALLED_APPS ga 'todos' qo'shing."
        )

    def test_allowed_hosts_not_empty(self):
        assert settings.ALLOWED_HOSTS, (
            "ALLOWED_HOSTS bo'sh.\n"
            f"{DJANGO_APP_DIR.name}/settings.py da ALLOWED_HOSTS = ['*'] deb yozing."
        )

    def test_allowed_hosts_accepts_connections(self):
        hosts = settings.ALLOWED_HOSTS
        allowed = '*' in hosts or 'localhost' in hosts or '127.0.0.1' in hosts
        assert allowed, (
            f"ALLOWED_HOSTS = {hosts}\n"
            "Kamida '*', 'localhost' yoki '127.0.0.1' bo'lishi kerak."
        )

    def test_initial_migration_exists(self):
        migrations_dir = BASE_DIR / 'todos' / 'migrations'
        if not migrations_dir.exists():
            pytest.fail(
                "todos/migrations/ papkasi yo'q. "
                "python manage.py startapp todos ni bajaring."
            )
        migration_files = [
            f for f in migrations_dir.iterdir()
            if f.name.startswith('0001') and f.suffix == '.py'
        ]
        assert migration_files, (
            "0001_initial.py migration fayli topilmadi.\n"
            "python manage.py makemigrations ni bajaring."
        )

    def test_database_file_exists(self):
        assert (BASE_DIR / 'db.sqlite3').exists(), (
            "db.sqlite3 topilmadi.\n"
            "python manage.py migrate ni bajaring."
        )
