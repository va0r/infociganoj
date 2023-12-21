from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models.course import Course, CourseSubscription
from users.models import User


class CourseUnsubscribeTestCase(APITestCase):
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
        self.course_subscription = CourseSubscription.objects.create(user=self.user, course=self.course)

    def test_unsubscribe_from_course(self):
        """
        Тест операции отписки от курса
        """
        unsubscribe_url = reverse('courses:course-unsubscribe', args=[self.course.id])
        response = self.client.delete(unsubscribe_url, format='json', **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseSubscription.objects.filter(id=self.course_subscription.id, is_active=True).exists())
