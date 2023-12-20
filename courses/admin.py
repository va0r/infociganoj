from django.contrib import admin

from courses.models.course import Course
from courses.models.lesson import Lesson

admin.site.register(Course)
admin.site.register(Lesson)
