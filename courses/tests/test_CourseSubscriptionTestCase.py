from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models.course import Course, CourseSubscription
from courses.serializer.course import CourseSerializer
from users.models import User


class CourseSubscriptionTestCase(APITestCase):
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
            description="test_description",
        )

    def test_str_method_returns(self):
        subscription = CourseSubscription.objects.create(user=self.user, course=self.course)
        self.assertEqual(str(subscription), f'{self.user}: {self.course}')

    def test_subscribe_to_course(self):
        """
        Тест операции создания подписки на курс
        """
        subscribe_url = reverse('courses:course-subscribe', args=[self.course.id])
        response = self.client.post(subscribe_url, {}, format='json', **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], "Подписка успешно установлена.")

    def test_subscribe_to_course_twice(self):
        """
        Тест, чтобы проверить, что пользователь не может подписаться на один курс дважды
        """
        CourseSubscription.objects.create(user=self.user, course=self.course)  # Создаем подписку
        subscribe_url = reverse('courses:course-subscribe', args=[self.course.id])
        response = self.client.post(subscribe_url, {}, format='json', **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Вы уже подписаны на этот курс.")

    def test_unauthenticated_user_cannot_subscribe(self):
        """
        Тест, чтобы проверить, что неавторизованный пользователь не может подписаться на курс
        """
        # Очищаем аутентификацию
        self.client.credentials()

        subscribe_url = reverse('courses:course-subscribe', args=[self.course.id])
        response = self.client.post(subscribe_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Учетные данные не были предоставлены.", str(response.data['detail']))

    def test_get_is_subscribed_for_anonymous_user(self):
        """
        Тест, чтобы проверить, что неавторизованный пользователь не может быть подписан на курс
        """
        # Создаем объект Request явно
        factory = RequestFactory()
        request = factory.get('/')

        # Удаляем аутентификацию пользователя
        request.user = AnonymousUser()

        # Создаем новый сериализатор с измененным контекстом
        serializer_unauthenticated = CourseSerializer(self.course, context={'request': request})

        # Проверяем, что is_subscribed возвращает False для неавторизованного пользователя
        self.assertFalse(serializer_unauthenticated.data['is_subscribed'])
