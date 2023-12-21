from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models.course import Course
from users.models import User


class CoursesTestCase(APITestCase):
    def setUp(self):
        # Тестовый пользователь
        self.user = User.objects.create(
            email='test@example.com',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        self.user.set_password('test')
        self.user.save()

        # Получаем JWT-токен для аутентификации
        get_token = reverse('users:token_obtain_pair')
        token_response = self.client.post(path=get_token, data={'email': 'test@example.com', 'password': 'test'})
        token = token_response.json().get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

        self.course_data = {'name': 'Test Course', 'description': 'Test Description'}
        self.course = Course.objects.create(**self.course_data)
        self.url = reverse('courses:courses-detail', kwargs={'pk': self.course.pk})

    def test_retrieve_course(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.course_data['name'])
        self.assertEqual(response.data['description'], self.course_data['description'])

    def test_retrieve_course_not_found(self):
        # Попытка получить несуществующий курс
        response = self.client.get(reverse('courses:courses-detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
