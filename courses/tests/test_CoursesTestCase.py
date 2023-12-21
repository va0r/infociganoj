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

    def test_create_course(self):
        new_course_data = {'name': 'New Course', 'description': 'New Course Description'}

        response = self.client.post(reverse('courses:courses-list'), data=new_course_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)  # Должен быть только один курс
        new_course = Course.objects.get(name=new_course_data['name'])
        self.assertEqual(response.data['name'], new_course.name)
        self.assertEqual(response.data['description'], new_course.description)

    def test_update_course(self):
        updated_course_data = {'name': 'Updated Course', 'description': 'Updated Course Description'}

        response = self.client.put(self.url, data=updated_course_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, updated_course_data['name'])
        self.assertEqual(self.course.description, updated_course_data['description'])

    def test_delete_course(self):
        response = self.client.delete(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())

    def test_perform_update(self):
        updated_course_data = {'name': 'Updated Course', 'description': 'Updated Course Description'}

        response = self.client.patch(self.url, data=updated_course_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, updated_course_data['name'])
        self.assertEqual(self.course.description, updated_course_data['description'])
