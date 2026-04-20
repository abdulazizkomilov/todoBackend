"""
2-dars — Model va Serializer
Tekshiriladi:
  1-qism: Todo modeli — fieldlar, parametrlar, ordering, __str__
  2-qism: TodoSerializer — fieldlar, read_only, writable, rest_framework
  3-qism: Admin — TodoAdmin ro'yxatdan o'tganmi, superuser yaratilganmi
"""
from pathlib import Path

import pytest
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ── 1-qism: Todo modeli ────────────────────────────────────────────────────

class TestTodoModel:
    def test_models_py_exists(self):
        assert (BASE_DIR / 'todos' / 'models.py').exists(), (
            "todos/models.py topilmadi."
        )

    def test_todo_model_importable(self):
        try:
            from todos.models import Todo  # noqa: F401
        except ImportError as e:
            pytest.fail(
                f"todos.models dan Todo import qilib bo'lmadi: {e}\n"
                "todos/models.py da Todo klassini yozdingizmi?"
            )

    def test_model_has_all_fields(self):
        from todos.models import Todo
        field_names = {f.name for f in Todo._meta.get_fields()}
        required = {'title', 'description', 'completed', 'created_at', 'updated_at'}
        missing = required - field_names
        assert not missing, (
            f"Todo modelida quyidagi fieldlar yo'q: {missing}\n"
            "todos/models.py ni tekshiring."
        )

    def test_title_is_charfield_with_max_length(self):
        from todos.models import Todo
        field = Todo._meta.get_field('title')
        assert field.get_internal_type() == 'CharField', (
            "title CharField bo'lishi kerak."
        )
        assert field.max_length >= 255, (
            f"title max_length=255 bo'lishi kerak, hozir: {field.max_length}"
        )

    def test_description_is_textfield_and_blank(self):
        from todos.models import Todo
        field = Todo._meta.get_field('description')
        assert field.get_internal_type() == 'TextField', (
            "description TextField bo'lishi kerak."
        )
        assert field.blank is True, (
            "description blank=True bo'lishi kerak."
        )
        assert field.default == '', (
            "description default='' bo'lishi kerak."
        )

    def test_completed_is_booleanfield_default_false(self):
        from todos.models import Todo
        field = Todo._meta.get_field('completed')
        assert field.get_internal_type() == 'BooleanField', (
            "completed BooleanField bo'lishi kerak."
        )
        assert field.default is False, (
            "completed default=False bo'lishi kerak."
        )

    def test_created_at_auto_now_add(self):
        from todos.models import Todo
        field = Todo._meta.get_field('created_at')
        assert field.auto_now_add is True, (
            "created_at auto_now_add=True bo'lishi kerak."
        )

    def test_updated_at_auto_now(self):
        from todos.models import Todo
        field = Todo._meta.get_field('updated_at')
        assert field.auto_now is True, (
            "updated_at auto_now=True bo'lishi kerak."
        )

    def test_ordering_newest_first(self):
        from todos.models import Todo
        assert list(Todo._meta.ordering) == ['-created_at'], (
            "Meta.ordering = ['-created_at'] bo'lishi kerak."
        )

    def test_str_returns_title(self):
        from todos.models import Todo
        todo = Todo(title="Mening birinchi todom")
        assert str(todo) == "Mening birinchi todom", (
            "__str__ metodi title ni qaytarishi kerak."
        )

    def test_migration_0001_exists(self):
        migrations_dir = BASE_DIR / 'todos' / 'migrations'
        files = [f.name for f in migrations_dir.iterdir() if f.suffix == '.py']
        has_initial = any(f.startswith('0001') for f in files)
        assert has_initial, (
            "0001_initial.py topilmadi.\n"
            "python manage.py makemigrations ni bajaring."
        )

    @pytest.mark.django_db
    def test_todo_can_be_created_in_db(self):
        from todos.models import Todo
        todo = Todo.objects.create(title="Test", description="Tavsif")
        assert todo.pk is not None, "Todo bazaga saqlanmadi."
        assert todo.completed is False
        assert todo.title == "Test"

    @pytest.mark.django_db
    def test_todo_ordering_in_db(self):
        from todos.models import Todo
        t1 = Todo.objects.create(title="Birinchi")
        t2 = Todo.objects.create(title="Ikkinchi")
        todos = list(Todo.objects.all())
        assert todos[0].id == t2.id, (
            "Eng yangi todo ro'yxat boshida turishi kerak (ordering = ['-created_at'])."
        )


# ── 2-qism: TodoSerializer ─────────────────────────────────────────────────

class TestTodoSerializer:
    def test_rest_framework_in_installed_apps(self):
        assert 'rest_framework' in settings.INSTALLED_APPS, (
            "'rest_framework' INSTALLED_APPS da yo'q.\n"
            "core/settings.py ga 'rest_framework' ni qo'shing."
        )

    def test_serializers_py_exists(self):
        assert (BASE_DIR / 'todos' / 'serializers.py').exists(), (
            "todos/serializers.py topilmadi.\n"
            "todos/ papkasida serializers.py fayl yarating."
        )

    def test_serializer_importable(self):
        try:
            from todos.serializers import TodoSerializer  # noqa: F401
        except ImportError as e:
            pytest.fail(
                f"TodoSerializer import qilib bo'lmadi: {e}\n"
                "todos/serializers.py da TodoSerializer klassini yozdingizmi?"
            )

    def test_serializer_has_all_fields(self):
        from todos.serializers import TodoSerializer
        fields = set(TodoSerializer().fields.keys())
        expected = {'id', 'title', 'description', 'completed', 'created_at', 'updated_at'}
        missing = expected - fields
        extra = fields - expected
        assert not missing, (
            f"Serializer da bu fieldlar yo'q: {missing}\n"
            "Meta.fields ro'yxatini tekshiring."
        )
        assert not extra, (
            f"Serializer da kutilmagan fieldlar bor: {extra}"
        )

    def test_id_is_readonly(self):
        from todos.serializers import TodoSerializer
        assert TodoSerializer().fields['id'].read_only, (
            "'id' read_only_fields da bo'lishi kerak."
        )

    def test_created_at_is_readonly(self):
        from todos.serializers import TodoSerializer
        assert TodoSerializer().fields['created_at'].read_only, (
            "'created_at' read_only_fields da bo'lishi kerak."
        )

    def test_updated_at_is_readonly(self):
        from todos.serializers import TodoSerializer
        assert TodoSerializer().fields['updated_at'].read_only, (
            "'updated_at' read_only_fields da bo'lishi kerak."
        )

    def test_title_is_writable(self):
        from todos.serializers import TodoSerializer
        assert not TodoSerializer().fields['title'].read_only, (
            "'title' yozilishi mumkin bo'lishi kerak (read_only emas)."
        )

    def test_completed_is_writable(self):
        from todos.serializers import TodoSerializer
        assert not TodoSerializer().fields['completed'].read_only, (
            "'completed' yozilishi mumkin bo'lishi kerak."
        )

    @pytest.mark.django_db
    def test_serializer_output_matches_model(self):
        from todos.models import Todo
        from todos.serializers import TodoSerializer
        todo = Todo.objects.create(title="Serializer testi", description="Tavsif")
        data = TodoSerializer(todo).data
        assert data['title'] == "Serializer testi"
        assert data['description'] == "Tavsif"
        assert data['completed'] is False
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data


# ── 3-qism: Admin ─────────────────────────────────────────────────────────

class TestTodoAdmin:
    def test_todo_registered_in_admin(self):
        from django.contrib import admin
        from todos.models import Todo
        assert admin.site.is_registered(Todo), (
            "Todo admin da ro'yxatdan o'tmagan.\n"
            "todos/admin.py da @admin.register(Todo) yoki "
            "admin.site.register(Todo) ni yozing."
        )

    def test_admin_list_display(self):
        from django.contrib import admin
        from todos.models import Todo
        todo_admin = admin.site._registry.get(Todo)
        assert todo_admin is not None
        for field in ('id', 'title', 'completed'):
            assert field in todo_admin.list_display, (
                f"list_display da '{field}' yo'q."
            )

    def test_admin_list_filter(self):
        from django.contrib import admin
        from todos.models import Todo
        todo_admin = admin.site._registry.get(Todo)
        assert todo_admin is not None
        assert 'completed' in todo_admin.list_filter, (
            "list_filter da 'completed' yo'q."
        )

    def test_admin_search_fields(self):
        from django.contrib import admin
        from todos.models import Todo
        todo_admin = admin.site._registry.get(Todo)
        assert todo_admin is not None
        assert todo_admin.search_fields, (
            "search_fields bo'sh. Kamida 'title' ni qo'shing."
        )
