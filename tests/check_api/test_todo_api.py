"""
Todo API endpointlarining to'g'ri ishlashini tekshiruvchi testlar.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from todos.models import Todo


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def todo(db):
    return Todo.objects.create(title="Test todo", description="Tavsif", completed=False)


@pytest.fixture
def completed_todo(db):
    return Todo.objects.create(title="Bajarilgan todo", completed=True)


# ── GET /api/todos/ ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTodoList:
    def test_list_returns_200(self, client):
        res = client.get(reverse('todo-list-create'))
        assert res.status_code == status.HTTP_200_OK

    def test_list_returns_all_todos(self, client, todo, completed_todo):
        res = client.get(reverse('todo-list-create'))
        assert len(res.data) == 2

    def test_list_empty_when_no_todos(self, client, db):
        res = client.get(reverse('todo-list-create'))
        assert res.data == []

    def test_list_ordered_by_newest_first(self, client, db):
        t1 = Todo.objects.create(title="Birinchi")
        t2 = Todo.objects.create(title="Ikkinchi")
        res = client.get(reverse('todo-list-create'))
        assert res.data[0]['id'] == t2.id
        assert res.data[1]['id'] == t1.id

    def test_list_response_fields(self, client, todo):
        res = client.get(reverse('todo-list-create'))
        item = res.data[0]
        for field in ('id', 'title', 'description', 'completed', 'created_at', 'updated_at'):
            assert field in item, f"Response da '{field}' maydoni yo'q"


# ── POST /api/todos/ ───────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTodoCreate:
    def test_create_returns_201(self, client):
        res = client.post(reverse('todo-list-create'), {'title': 'Yangi todo'})
        assert res.status_code == status.HTTP_201_CREATED

    def test_create_saves_to_database(self, client):
        client.post(reverse('todo-list-create'), {'title': 'DB testi'})
        assert Todo.objects.filter(title='DB testi').exists()

    def test_create_with_title_and_description(self, client):
        res = client.post(reverse('todo-list-create'), {
            'title': 'Sarlavha',
            'description': 'Tavsif matni',
        })
        assert res.data['title'] == 'Sarlavha'
        assert res.data['description'] == 'Tavsif matni'

    def test_create_completed_defaults_to_false(self, client):
        res = client.post(reverse('todo-list-create'), {'title': 'Default holat'})
        assert res.data['completed'] is False

    def test_create_without_title_returns_400(self, client):
        res = client.post(reverse('todo-list-create'), {'description': 'Sarlavsiz'})
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_returns_id_and_timestamps(self, client):
        res = client.post(reverse('todo-list-create'), {'title': 'Vaqt testi'})
        assert 'id' in res.data
        assert 'created_at' in res.data
        assert 'updated_at' in res.data


# ── GET /api/todos/<id>/ ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestTodoRetrieve:
    def test_retrieve_returns_200(self, client, todo):
        res = client.get(reverse('todo-detail', kwargs={'pk': todo.pk}))
        assert res.status_code == status.HTTP_200_OK

    def test_retrieve_returns_correct_todo(self, client, todo):
        res = client.get(reverse('todo-detail', kwargs={'pk': todo.pk}))
        assert res.data['id'] == todo.id
        assert res.data['title'] == todo.title

    def test_retrieve_nonexistent_returns_404(self, client, db):
        res = client.get(reverse('todo-detail', kwargs={'pk': 9999}))
        assert res.status_code == status.HTTP_404_NOT_FOUND


# ── PUT /api/todos/<id>/ ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestTodoUpdate:
    def test_put_returns_200(self, client, todo):
        res = client.put(
            reverse('todo-detail', kwargs={'pk': todo.pk}),
            {'title': 'Yangilangan', 'description': '', 'completed': False},
        )
        assert res.status_code == status.HTTP_200_OK

    def test_put_updates_title(self, client, todo):
        client.put(
            reverse('todo-detail', kwargs={'pk': todo.pk}),
            {'title': 'O\'zgartirilgan sarlavha', 'description': '', 'completed': False},
        )
        todo.refresh_from_db()
        assert todo.title == "O'zgartirilgan sarlavha"

    def test_put_without_title_returns_400(self, client, todo):
        res = client.put(
            reverse('todo-detail', kwargs={'pk': todo.pk}),
            {'description': 'Sarlavsiz'},
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST


# ── PATCH /api/todos/<id>/ ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestTodoPatch:
    def test_patch_returns_200(self, client, todo):
        res = client.patch(
            reverse('todo-detail', kwargs={'pk': todo.pk}),
            {'completed': True},
        )
        assert res.status_code == status.HTTP_200_OK

    def test_patch_updates_completed(self, client, todo):
        client.patch(reverse('todo-detail', kwargs={'pk': todo.pk}), {'completed': True})
        todo.refresh_from_db()
        assert todo.completed is True

    def test_patch_updates_title_only(self, client, todo):
        original_desc = todo.description
        client.patch(reverse('todo-detail', kwargs={'pk': todo.pk}), {'title': 'Faqat sarlavha'})
        todo.refresh_from_db()
        assert todo.title == 'Faqat sarlavha'
        assert todo.description == original_desc

    def test_patch_nonexistent_returns_404(self, client, db):
        res = client.patch(reverse('todo-detail', kwargs={'pk': 9999}), {'title': 'Yo\'q'})
        assert res.status_code == status.HTTP_404_NOT_FOUND


# ── DELETE /api/todos/<id>/ ────────────────────────────────────────────────

@pytest.mark.django_db
class TestTodoDelete:
    def test_delete_returns_204(self, client, todo):
        res = client.delete(reverse('todo-detail', kwargs={'pk': todo.pk}))
        assert res.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_removes_from_database(self, client, todo):
        pk = todo.pk
        client.delete(reverse('todo-detail', kwargs={'pk': pk}))
        assert not Todo.objects.filter(pk=pk).exists()

    def test_delete_nonexistent_returns_404(self, client, db):
        res = client.delete(reverse('todo-detail', kwargs={'pk': 9999}))
        assert res.status_code == status.HTTP_404_NOT_FOUND


# ── PATCH /api/todos/<id>/toggle/ ─────────────────────────────────────────

@pytest.mark.django_db
class TestTodoToggle:
    def test_toggle_returns_200(self, client, todo):
        res = client.patch(reverse('todo-toggle', kwargs={'pk': todo.pk}))
        assert res.status_code == status.HTTP_200_OK

    def test_toggle_false_to_true(self, client, todo):
        assert todo.completed is False
        client.patch(reverse('todo-toggle', kwargs={'pk': todo.pk}))
        todo.refresh_from_db()
        assert todo.completed is True

    def test_toggle_true_to_false(self, client, completed_todo):
        assert completed_todo.completed is True
        client.patch(reverse('todo-toggle', kwargs={'pk': completed_todo.pk}))
        completed_todo.refresh_from_db()
        assert completed_todo.completed is False

    def test_toggle_twice_restores_original(self, client, todo):
        url = reverse('todo-toggle', kwargs={'pk': todo.pk})
        client.patch(url)
        client.patch(url)
        todo.refresh_from_db()
        assert todo.completed is False

    def test_toggle_returns_updated_data(self, client, todo):
        res = client.patch(reverse('todo-toggle', kwargs={'pk': todo.pk}))
        assert res.data['completed'] is True
        assert res.data['id'] == todo.id

    def test_toggle_nonexistent_returns_404(self, client, db):
        res = client.patch(reverse('todo-toggle', kwargs={'pk': 9999}))
        assert res.status_code == status.HTTP_404_NOT_FOUND
