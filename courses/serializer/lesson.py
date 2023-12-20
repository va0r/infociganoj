from rest_framework import serializers

from courses.models.lesson import Lesson
from courses.serializer.course import CourseSerializer
from courses.validators import ValidateYoutubeLinks


class LessonSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
    validators = [ValidateYoutubeLinks(field='video_url')]

    class Meta:
        model = Lesson
        fields = '__all__'
