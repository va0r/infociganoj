from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models.course import Course
from courses.models.lesson import Lesson
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        # Тестовый пользователь
        self.user = User.objects.create(
            email='test@example.com',
            is_active=True
        )
        self.user.set_password('test')
        self.user.save()

        # Получаем JWT-токен для аутентификации
        get_token = reverse('users:token_obtain_pair')
        token_response = self.client.post(path=get_token, data={'email': 'test@example.com', 'password': 'test'})
        token = token_response.json().get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

        self.course = Course.objects.create(
            name="test_course",
        )

        # Создаем тестовый урок
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="This is a test lesson",
            owner=self.user
        )

    def test_create_lesson(self):
        """
        Тест операции создания (create) проверки создания уроков
        """
        data = {
            "name": "test",
            "course": 1,
            "link": "https://youtube.com",
            "description": "test description"
        }
        create_lesson = reverse('courses:lesson-create')
        response = self.client.post(create_lesson, data, format='json', **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data['name'])

    def test_retrieve_lesson(self):
        """
        Тест операции чтения (retrieve) урока
        """
        retrieve_url = reverse('courses:lesson-get', args=[self.lesson.id])
        response = self.client.get(retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.lesson.name)
        self.assertEqual(str(self.lesson), 'Test Lesson: This is a test lesson')

    def test_update_lesson(self):
        # Тест операции обновления (update) урока
        update_url = reverse('courses:lesson-update', args=[self.lesson.id])
        updated_data = {
            "name": "Updated Lesson",
            "description": "This is an updated lesson",
        }
        response = self.client.patch(update_url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, updated_data['name'])
        self.assertEqual(self.lesson.description, updated_data['description'])

    def test_delete_lesson(self):
        # Тест операции удаления (delete) урока
        delete_url = reverse('courses:lesson-destroy', args=[self.lesson.id])
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())
