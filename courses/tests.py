from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase, force_authenticate, APIRequestFactory
from rest_framework.views import APIView

from courses.models.course import Course, CourseSubscription
from courses.models.lesson import Lesson
from courses.permissions import IsModerator
from courses.validators import ValidateYoutubeLinks
from users.models import User, UserRoles


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


class ValidateYoutubeLinksTest(APITestCase):
    def test_valid_url(self):
        validator = ValidateYoutubeLinks('videos')
        value = {'videos': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}
        errors = validator(value)
        self.assertEqual(errors, None)

    def test_empty_value(self):
        validator = ValidateYoutubeLinks('videos')
        value = {}
        errors = validator(value)
        self.assertEqual(errors, None)


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

    class IsModeratorPermissionTestCase(APITestCase):
        def setUp(self):
            self.factory = APIRequestFactory()
            self.course_data = {'name': 'Test Course', 'description': 'Test Description'}
            self.course = Course.objects.create(**self.course_data)
            self.user = get_user_model().objects.create(email='testuser@test.user',
                                                        password='testpassword',
                                                        role=UserRoles.MODERATOR)
            self.other_user = get_user_model().objects.create(email='otheruser@other.user',
                                                              password='otherpassword',
                                                              role=UserRoles.MEMBER)
            self.url = reverse('courses:courses-detail', kwargs={'pk': self.course.pk})

        class CustomView(APIView):
            permission_classes = [IsModerator]

            def get(self, request, *args, **kwargs):
                return HttpResponse(status=status.HTTP_200_OK)

            def put(self, request, *args, **kwargs):
                return HttpResponse(status=status.HTTP_200_OK)

            def patch(self, request, *args, **kwargs):
                return HttpResponse(status=status.HTTP_200_OK)

            def post(self, request, *args, **kwargs):
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)

            def delete(self, request, *args, **kwargs):
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        def test_is_moderator_permission_allowed_methods(self):
            view = self.CustomView.as_view()

            request_get = self.factory.get(self.url)
            force_authenticate(request_get, user=self.user)
            response_get = view(request_get)
            self.assertEqual(response_get.status_code, status.HTTP_200_OK)

            request_put = self.factory.put(self.url)
            force_authenticate(request_put, user=self.user)
            response_put = view(request_put)
            self.assertEqual(response_put.status_code, status.HTTP_200_OK)

            request_patch = self.factory.patch(self.url)
            force_authenticate(request_patch, user=self.user)
            response_patch = view(request_patch)
            self.assertEqual(response_patch.status_code, status.HTTP_200_OK)

        def test_is_moderator_permission_denied_methods(self):
            view = self.CustomView.as_view()

            request_post = self.factory.post(self.url)
            force_authenticate(request_post, user=self.user)
            response_post = view(request_post)
            self.assertEqual(response_post.status_code, status.HTTP_403_FORBIDDEN)

            request_delete = self.factory.delete(self.url)
            force_authenticate(request_delete, user=self.user)
            response_delete = view(request_delete)
            self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)
