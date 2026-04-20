"""
Loyiha setup to'g'ri sozlanganligini tekshiruvchi testlar.

Ushbu testlar Django 5.x, 6.x va undan yuqori versiyalarda,
Python 3.12+ da ishlash uchun mo'ljallangan.
"""
import sys
import django
import pytest
from django.conf import settings


# # ── 1. Python versiyasi ────────────────────────────────────────────────────

# class TestPythonVersion:
#     def test_python_version_3_12_or_higher(self):
#         major, minor = sys.version_info.major, sys.version_info.minor
#         assert (major, minor) >= (3, 12), (
#             f"Python 3.12+ talab qilinadi, hozir: {major}.{minor}"
#         )


# ── 2. Django versiyasi ────────────────────────────────────────────────────

class TestDjangoVersion:
    def test_django_version_5_or_higher(self):
        major = int(django.__version__.split('.')[0])
        assert major >= 5, (
            f"Django 5.x yoki yuqori versiya kerak, hozir: {django.__version__}"
        )


# ── 3. O'rnatilgan paketlar ────────────────────────────────────────────────

class TestInstalledApps:
    def test_rest_framework_installed(self):
        assert 'rest_framework' in settings.INSTALLED_APPS, (
            "rest_framework INSTALLED_APPS ga qo'shilmagan. "
            "pip install djangorestframework && settings.py ga 'rest_framework' qo'shing."
        )

    def test_corsheaders_installed(self):
        assert 'corsheaders' in settings.INSTALLED_APPS, (
            "corsheaders INSTALLED_APPS ga qo'shilmagan. "
            "pip install django-cors-headers && settings.py ga 'corsheaders' qo'shing."
        )

    def test_todos_app_installed(self):
        assert 'todos' in settings.INSTALLED_APPS, (
            "'todos' app INSTALLED_APPS ga qo'shilmagan."
        )


# ── 4. Middleware tartib ───────────────────────────────────────────────────

class TestMiddleware:
    def test_cors_middleware_present(self):
        assert 'corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE, (
            "CorsMiddleware MIDDLEWARE da yo'q."
        )

    def test_cors_middleware_before_common(self):
        mw = list(settings.MIDDLEWARE)
        assert 'corsheaders.middleware.CorsMiddleware' in mw, "CorsMiddleware yo'q"
        assert 'django.middleware.common.CommonMiddleware' in mw, "CommonMiddleware yo'q"
        cors_idx = mw.index('corsheaders.middleware.CorsMiddleware')
        common_idx = mw.index('django.middleware.common.CommonMiddleware')
        assert cors_idx < common_idx, (
            "CorsMiddleware CommonMiddleware dan OLDIN turishi shart "
            f"(hozir: cors={cors_idx}, common={common_idx})"
        )

    def test_session_middleware_present(self):
        assert 'django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE


# ── 5. CORS sozlamalari ────────────────────────────────────────────────────

class TestCorsSettings:
    def test_cors_origins_configured(self):
        # CORS_ALLOWED_ORIGINS yoki CORS_ALLOW_ALL_ORIGINS dan biri bo'lishi kerak
        has_origins = bool(getattr(settings, 'CORS_ALLOWED_ORIGINS', []))
        has_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        assert has_origins or has_all, (
            "CORS sozlanmagan. settings.py da CORS_ALLOWED_ORIGINS yoki "
            "CORS_ALLOW_ALL_ORIGINS = True qo'shing."
        )

    def test_localhost_3000_allowed(self):
        # CORS_ALLOW_ALL_ORIGINS=True bo'lsa bu test o'tkazib yuboriladi
        if getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False):
            pytest.skip("CORS_ALLOW_ALL_ORIGINS=True, barcha originlarga ruxsat berilgan")
        origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        assert 'http://localhost:3000' in origins, (
            "http://localhost:3000 CORS_ALLOWED_ORIGINS da yo'q"
        )


# ── 6. Database ────────────────────────────────────────────────────────────

class TestDatabase:
    def test_database_configured(self):
        assert 'default' in settings.DATABASES, (
            "DATABASES['default'] sozlanmagan."
        )

    def test_sqlite_engine(self):
        engine = settings.DATABASES['default']['ENGINE']
        assert engine == 'django.db.backends.sqlite3', (
            f"SQLite engine kutilgan, hozir: {engine}"
        )


# ── 7. URL yo'naltirishlar ─────────────────────────────────────────────────

class TestUrlConfiguration:
    def test_todos_list_url(self):
        from django.urls import reverse, NoReverseMatch
        try:
            url = reverse('todo-list-create')
            assert url == '/api/todos/'
        except NoReverseMatch:
            pytest.fail(
                "'todo-list-create' URL topilmadi.\n"
                "config/urls.py ga quyidagini qo'shing:\n"
                "  path('api/todos/', include('todos.urls'))"
            )

    def test_todos_detail_url(self):
        from django.urls import reverse, NoReverseMatch
        try:
            url = reverse('todo-detail', kwargs={'pk': 1})
            assert url == '/api/todos/1/'
        except NoReverseMatch:
            pytest.fail("'todo-detail' URL topilmadi.")

    def test_todos_toggle_url(self):
        from django.urls import reverse, NoReverseMatch
        try:
            url = reverse('todo-toggle', kwargs={'pk': 1})
            assert url == '/api/todos/1/toggle/'
        except NoReverseMatch:
            pytest.fail("'todo-toggle' URL topilmadi.")


# ── 8. Model mavjudligi ────────────────────────────────────────────────────

class TestTodoModel:
    def test_model_importable(self):
        try:
            from todos.models import Todo  # noqa: F401
        except ImportError as e:
            pytest.fail(f"todos.models dan Todo import qilib bo'lmadi: {e}")

    def test_model_has_required_fields(self):
        from todos.models import Todo
        field_names = {f.name for f in Todo._meta.get_fields()}
        required = {'title', 'description', 'completed', 'created_at', 'updated_at'}
        missing = required - field_names
        assert not missing, f"Todo modelida quyidagi fieldlar yo'q: {missing}"

    def test_title_max_length(self):
        from todos.models import Todo
        field = Todo._meta.get_field('title')
        assert field.max_length >= 255, (
            f"title max_length kamida 255 bo'lishi kerak, hozir: {field.max_length}"
        )

    def test_description_blank_allowed(self):
        from todos.models import Todo
        field = Todo._meta.get_field('description')
        assert field.blank is True, "description maydoni blank=True bo'lishi kerak"

    def test_completed_default_false(self):
        from todos.models import Todo
        field = Todo._meta.get_field('completed')
        assert field.default is False, "completed default=False bo'lishi kerak"

    def test_model_ordering_newest_first(self):
        from todos.models import Todo
        ordering = list(Todo._meta.ordering)
        assert ordering == ['-created_at'], (
            f"ordering = ['-created_at'] bo'lishi kerak, hozir: {ordering}"
        )

    def test_model_str(self):
        from todos.models import Todo
        todo = Todo(title="Test sarlavha")
        assert str(todo) == "Test sarlavha"


# ── 9. Serializer mavjudligi ───────────────────────────────────────────────

class TestTodoSerializer:
    def test_serializer_importable(self):
        try:
            from todos.serializers import TodoSerializer  # noqa: F401
        except ImportError as e:
            pytest.fail(f"todos.serializers dan TodoSerializer import qilib bo'lmadi: {e}")

    def test_serializer_has_all_fields(self):
        from todos.serializers import TodoSerializer
        fields = set(TodoSerializer().fields.keys())
        expected = {'id', 'title', 'description', 'completed', 'created_at', 'updated_at'}
        missing = expected - fields
        extra = fields - expected
        assert not missing, f"Serializer da bu fieldlar yo'q: {missing}"
        assert not extra, f"Serializer da kutilmagan fieldlar bor: {extra}"

    def test_readonly_fields(self):
        from todos.serializers import TodoSerializer
        s = TodoSerializer()
        for name in ('id', 'created_at', 'updated_at'):
            assert s.fields[name].read_only, (
                f"'{name}' read_only=True bo'lishi kerak"
            )

    def test_writable_fields(self):
        from todos.serializers import TodoSerializer
        s = TodoSerializer()
        for name in ('title', 'description', 'completed'):
            assert not s.fields[name].read_only, (
                f"'{name}' write qilish mumkin bo'lishi kerak (read_only=False)"
            )
