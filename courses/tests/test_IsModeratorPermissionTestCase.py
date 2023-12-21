from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate, APIRequestFactory
from rest_framework.views import APIView

from courses.models.course import Course
from courses.permissions import IsModerator
from users.models import UserRoles


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

        @staticmethod
        def get(request, *args, **kwargs):
            return HttpResponse(status=status.HTTP_200_OK)

        @staticmethod
        def put(request, *args, **kwargs):
            return HttpResponse(status=status.HTTP_200_OK)

        @staticmethod
        def patch(request, *args, **kwargs):
            return HttpResponse(status=status.HTTP_200_OK)

        @staticmethod
        def post(request, *args, **kwargs):
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        @staticmethod
        def delete(request, *args, **kwargs):
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    def test_is_moderator_permission_allowed_methods(self):
        view = self.CustomView.as_view()

        request_get = self.factory.get(self.url)
        force_authenticate(request_get, user=self.user)
        response_get = view(request_get)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

        request_get = self.factory.get(self.url)
        force_authenticate(request_get, user=self.other_user)
        response_get = view(request_get)
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)

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
