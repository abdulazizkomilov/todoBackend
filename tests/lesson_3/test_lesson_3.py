"""
3-dars — Views, URLs va CORS
Tekshiriladi:
  1-qism: Views — TodoListCreateView, TodoDetailView, TodoToggleView
  2-qism: URLs — todos/urls.py, core/urls.py ga ulangan, URL nomlar
  3-qism: CORS — corsheaders, CorsMiddleware tartibi, CORS_ALLOWED_ORIGINS
"""
from pathlib import Path

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse, NoReverseMatch

from todos.models import Todo

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DJANGO_APP_DIR = (
    BASE_DIR / 'core' if (BASE_DIR / 'core').is_dir()
    else BASE_DIR / 'config'
)


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def todo(db):
    return Todo.objects.create(title="Test todo", description="Tavsif", completed=False)

@pytest.fixture
def completed_todo(db):
    return Todo.objects.create(title="Bajarilgan todo", completed=True)


# ── 1-qism: Views ──────────────────────────────────────────────────────────

class TestViewsExist:
    def test_views_py_exists(self):
        assert (BASE_DIR / 'todos' / 'views.py').exists(), (
            "todos/views.py topilmadi."
        )

    def test_list_create_view_importable(self):
        try:
            from todos.views import TodoListCreateView  # noqa: F401
        except ImportError as e:
            pytest.fail(
                f"TodoListCreateView import qilib bo'lmadi: {e}\n"
                "todos/views.py da TodoListCreateView klassini yozdingizmi?"
            )

    def test_detail_view_importable(self):
        try:
            from todos.views import TodoDetailView  # noqa: F401
        except ImportError as e:
            pytest.fail(
                f"TodoDetailView import qilib bo'lmadi: {e}\n"
                "todos/views.py da TodoDetailView klassini yozdingizmi?"
            )

    def test_toggle_view_importable(self):
        try:
            from todos.views import TodoToggleView  # noqa: F401
        except ImportError as e:
            pytest.fail(
                f"TodoToggleView import qilib bo'lmadi: {e}\n"
                "todos/views.py da TodoToggleView klassini yozdingizmi?"
            )

    def test_list_create_view_uses_correct_queryset(self):
        from todos.views import TodoListCreateView
        assert hasattr(TodoListCreateView, 'queryset'), (
            "TodoListCreateView da queryset yo'q."
        )

    def test_list_create_view_uses_serializer(self):
        from todos.views import TodoListCreateView
        from todos.serializers import TodoSerializer
        assert TodoListCreateView.serializer_class is TodoSerializer, (
            "TodoListCreateView serializer_class = TodoSerializer bo'lishi kerak."
        )

    def test_detail_view_uses_serializer(self):
        from todos.views import TodoDetailView
        from todos.serializers import TodoSerializer
        assert TodoDetailView.serializer_class is TodoSerializer, (
            "TodoDetailView serializer_class = TodoSerializer bo'lishi kerak."
        )


@pytest.mark.django_db
class TestListCreateAPI:
    def test_get_list_returns_200(self, client):
        res = client.get(reverse('todo-list-create'))
        assert res.status_code == status.HTTP_200_OK

    def test_post_creates_todo(self, client):
        res = client.post(reverse('todo-list-create'), {'title': 'Yangi todo'})
        assert res.status_code == status.HTTP_201_CREATED
        assert Todo.objects.filter(title='Yangi todo').exists()

    def test_post_without_title_returns_400(self, client):
        res = client.post(reverse('todo-list-create'), {'description': 'Sarlavsiz'})
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_returns_all_todos(self, client, todo, completed_todo):
        res = client.get(reverse('todo-list-create'))
        assert len(res.data) == 2

    def test_list_response_has_required_fields(self, client, todo):
        res = client.get(reverse('todo-list-create'))
        item = res.data[0]
        for field in ('id', 'title', 'description', 'completed', 'created_at', 'updated_at'):
            assert field in item, f"Response da '{field}' maydoni yo'q."


@pytest.mark.django_db
class TestDetailAPI:
    def test_get_single_todo_returns_200(self, client, todo):
        res = client.get(reverse('todo-detail', kwargs={'pk': todo.pk}))
        assert res.status_code == status.HTTP_200_OK
        assert res.data['id'] == todo.id

    def test_patch_updates_title(self, client, todo):
        res = client.patch(
            reverse('todo-detail', kwargs={'pk': todo.pk}),
            {'title': 'Yangilangan'},
        )
        assert res.status_code == status.HTTP_200_OK
        todo.refresh_from_db()
        assert todo.title == 'Yangilangan'

    def test_put_updates_todo(self, client, todo):
        res = client.put(
            reverse('todo-detail', kwargs={'pk': todo.pk}),
            {'title': 'To\'liq yangilash', 'description': '', 'completed': False},
        )
        assert res.status_code == status.HTTP_200_OK

    def test_delete_returns_204(self, client, todo):
        res = client.delete(reverse('todo-detail', kwargs={'pk': todo.pk}))
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert not Todo.objects.filter(pk=todo.pk).exists()

    def test_get_nonexistent_returns_404(self, client, db):
        res = client.get(reverse('todo-detail', kwargs={'pk': 9999}))
        assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestToggleAPI:
    def test_toggle_returns_200(self, client, todo):
        res = client.patch(reverse('todo-toggle', kwargs={'pk': todo.pk}))
        assert res.status_code == status.HTTP_200_OK

    def test_toggle_false_to_true(self, client, todo):
        client.patch(reverse('todo-toggle', kwargs={'pk': todo.pk}))
        todo.refresh_from_db()
        assert todo.completed is True

    def test_toggle_true_to_false(self, client, completed_todo):
        client.patch(reverse('todo-toggle', kwargs={'pk': completed_todo.pk}))
        completed_todo.refresh_from_db()
        assert completed_todo.completed is False

    def test_toggle_nonexistent_returns_404(self, client, db):
        res = client.patch(reverse('todo-toggle', kwargs={'pk': 9999}))
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_toggle_returns_updated_data(self, client, todo):
        res = client.patch(reverse('todo-toggle', kwargs={'pk': todo.pk}))
        assert res.data['completed'] is True
        assert res.data['id'] == todo.id


# ── 2-qism: URLs ──────────────────────────────────────────────────────────

class TestUrls:
    def test_todos_urls_py_exists(self):
        assert (BASE_DIR / 'todos' / 'urls.py').exists(), (
            "todos/urls.py topilmadi.\n"
            "todos/ papkasida urls.py fayl yarating."
        )

    def test_todo_list_create_url_name(self):
        try:
            url = reverse('todo-list-create')
            assert url == '/api/todos/'
        except NoReverseMatch:
            pytest.fail(
                "'todo-list-create' URL topilmadi.\n"
                "todos/urls.py: path('', ..., name='todo-list-create')\n"
                f"{DJANGO_APP_DIR.name}/urls.py: path('api/todos/', include('todos.urls'))"
            )

    def test_todo_detail_url_name(self):
        try:
            url = reverse('todo-detail', kwargs={'pk': 1})
            assert url == '/api/todos/1/'
        except NoReverseMatch:
            pytest.fail(
                "'todo-detail' URL topilmadi.\n"
                "todos/urls.py: path('<int:pk>/', ..., name='todo-detail')"
            )

    def test_todo_toggle_url_name(self):
        try:
            url = reverse('todo-toggle', kwargs={'pk': 1})
            assert url == '/api/todos/1/toggle/'
        except NoReverseMatch:
            pytest.fail(
                "'todo-toggle' URL topilmadi.\n"
                "todos/urls.py: path('<int:pk>/toggle/', ..., name='todo-toggle')"
            )

    def test_todos_included_in_main_urls(self):
        try:
            reverse('todo-list-create')
        except NoReverseMatch:
            pytest.fail(
                "todos URL lari asosiy urls.py ga ulanmagan.\n"
                f"{DJANGO_APP_DIR.name}/urls.py ga qo'shing:\n"
                "  path('api/todos/', include('todos.urls'))"
            )


# ── 3-qism: CORS ───────────────────────────────────────────────────────────

class TestCors:
    def test_corsheaders_in_installed_apps(self):
        assert 'corsheaders' in settings.INSTALLED_APPS, (
            "'corsheaders' INSTALLED_APPS da yo'q.\n"
            f"{DJANGO_APP_DIR.name}/settings.py ga 'corsheaders' ni qo'shing."
        )

    def test_cors_middleware_present(self):
        assert 'corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE, (
            "CorsMiddleware MIDDLEWARE da yo'q.\n"
            f"{DJANGO_APP_DIR.name}/settings.py dagi MIDDLEWARE ga qo'shing:\n"
            "  'corsheaders.middleware.CorsMiddleware'"
        )

    def test_cors_middleware_before_common(self):
        mw = list(settings.MIDDLEWARE)
        cors_idx = mw.index('corsheaders.middleware.CorsMiddleware')
        common_idx = mw.index('django.middleware.common.CommonMiddleware')
        assert cors_idx < common_idx, (
            "CorsMiddleware CommonMiddleware dan OLDIN turishi shart.\n"
            f"Hozir: CorsMiddleware={cors_idx}, CommonMiddleware={common_idx}"
        )

    def test_cors_origins_configured(self):
        has_origins = bool(getattr(settings, 'CORS_ALLOWED_ORIGINS', []))
        has_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        assert has_origins or has_all, (
            "CORS sozlanmagan.\n"
            f"{DJANGO_APP_DIR.name}/settings.py ga qo'shing:\n"
            "  CORS_ALLOWED_ORIGINS = ['http://localhost:3000']"
        )

    def test_cors_allows_localhost_3000(self):
        if getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False):
            pytest.skip("CORS_ALLOW_ALL_ORIGINS=True, barcha originlarga ruxsat berilgan.")
        origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        assert 'http://localhost:3000' in origins, (
            "http://localhost:3000 CORS_ALLOWED_ORIGINS da yo'q.\n"
            "Frontend localhost:3000 da ishlaydi, shu origin ruxsat etilishi kerak."
        )
