from django.db import models
from django.utils import timezone

from constants import NULLABLE


class Course(models.Model):
    name = models.CharField(max_length=150, verbose_name='course')
    preview = models.ImageField(verbose_name='preview', **NULLABLE)
    description = models.TextField(verbose_name='description')
    lessons = models.ManyToManyField('Lesson')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (f'{self.name}'
                f'{self.description}')

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


class CourseSubscription(models.Model):
    is_active = models.BooleanField(default=True, verbose_name='is_active')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name='curs_subsections')
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user}: {self.course}'

    class Meta:
        unique_together = [['user', 'course']]
        verbose_name = 'subscriptions'
        verbose_name_plural = 'subscriptions'
