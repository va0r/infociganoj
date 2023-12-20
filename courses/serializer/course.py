from rest_framework import serializers

from courses.models.course import Course, CourseSubscription
from courses.models.lesson import Lesson


class CourseSerializer(serializers.ModelSerializer):
    lessons = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all(), many=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Проверяем, подписан ли текущий пользователь на данный курс
            return CourseSubscription.objects.filter(user=request.user, course=obj, is_active=True).exists()
        return False  # Если пользователь не аутентифицирован, считаем, что он не подписан


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSubscription
        fields = '__all__'
