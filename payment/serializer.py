from rest_framework import serializers

from courses.models.course import Course
from courses.models.lesson import Lesson
from payment.models import Payment
from users.models import User


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = '__all__'


class PaymentCreateSerializer(serializers.ModelSerializer):
    paid_lesson = serializers.SlugRelatedField(slug_field='name', queryset=Lesson.objects.all(),
                                               allow_null=True, required=False),
    paid_course = serializers.SlugRelatedField(slug_field='name', queryset=Course.objects.all(),
                                               allow_null=True, required=False),
    user = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all()),

    class Meta:
        model = Payment
        fields = [
            'payment_amount',
            'paid_lesson',
            'paid_course',
            'payment_method',
            'user'
        ]
