from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models.course import Course, CourseSubscription
from courses.models.lesson import Lesson
from courses.permissions import IsOwner, IsModerator
from courses.serializer.course import CourseSerializer, CourseSubscriptionSerializer
from courses.serializer.lesson import LessonSerializer
from .tasks import send_subscription_notification, send_unsubscription_notification, send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [IsOwner | IsModerator]  # Применяем разрешения

    def perform_update(self, serializer):
        instance = serializer.save()
        # Обновляем дату последнего обновления курса
        instance.last_updated = timezone.now()
        instance.save()

        # Получаем список пользователей, подписанных на этот курс
        subscriptions = CourseSubscription.objects.filter(
            course=instance,
            is_active=True
        )

        # Создаем список адресов электронной почты пользователей
        user_emails = [subscription.user.email for subscription in subscriptions]

        # Запускаем задачу отправки уведомления об обновлении курса
        send_course_update_notification.delay(instance.name, user_emails)


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsOwner]  # Применяем разрешения


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]  # Применяем разрешения


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]  # Применяем разрешения


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]  # Применяем разрешения


class LessonDestroyAPIView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner]  # Применяем разрешения


class CourseSubscribeAPIView(generics.CreateAPIView):
    serializer_class = CourseSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.all()

    def create(self, request, *args, **kwargs):
        course = self.get_object()  # Получаем объект курса из URL
        user = request.user

        # Проверяем не подписан ли пользователь уже на этот курс
        if CourseSubscription.objects.filter(user=user, course=course, is_active=True).exists():
            return Response({"detail": "Вы уже подписаны на этот курс."}, status=status.HTTP_400_BAD_REQUEST)
        # Создаем подписку
        subscription = CourseSubscription(user=user, course=course)
        subscription.save()

        # Отправляем уведомление об успешной подписке пользователю
        send_subscription_notification.delay(user.email, course.name)

        return Response({"detail": "Подписка успешно установлена."}, status=status.HTTP_201_CREATED)


class CourseUnsubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        user = request.user
        # Устанавливаем подписку как неактивную вместо фактического удаления
        subscription = CourseSubscription.objects.filter(course=course_id, user=user).first()
        subscription.is_active = False
        subscription.save()

        # Отправляем уведомление об успешной отписке пользователю
        send_unsubscription_notification.delay(subscription.user.email, subscription.course.name)

        return Response({"detail": "Вы отписаны."}, status=status.HTTP_201_CREATED)
