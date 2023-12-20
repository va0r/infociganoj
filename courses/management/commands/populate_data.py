import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from courses.models.course import Course, CourseSubscription
from courses.models.lesson import Lesson
from payment.models import Payment


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Create courses with custom names
        course_data = [
            {'name': 'Python Basics',
             'lessons': ['Introduction', 'Variables', 'Control Flow', 'Functions', 'Data Structures', 'Modules',
                         'Error Handling', 'File Handling', 'Object-Oriented Programming', 'Final Project']},
            {'name': 'Web Development',
             'lessons': ['HTML', 'CSS', 'JavaScript', 'Frontend Frameworks', 'Backend Development', 'Databases',
                         'APIs', 'Authentication', 'Deployment', 'Final Project']},
            {'name': 'Data Science',
             'lessons': ['Introduction to Data Science', 'Data Exploration', 'Data Cleaning', 'Statistics',
                         'Machine Learning', 'Deep Learning', 'Data Visualization', 'Big Data', 'Model Evaluation',
                         'Final Project']}
        ]

        for course_info in course_data:
            course = Course.objects.create(name=course_info['name'], description=f'Description for {course_info["name"]}')
            self.stdout.write(self.style.SUCCESS(f'Course {course_info["name"]} created'))

            # Create lessons for each course
            for lesson_name in course_info['lessons']:
                lesson = Lesson.objects.create(
                    name=f'{lesson_name} for {course_info["name"]}',
                    description=f'Description for {lesson_name} of {course_info["name"]}',
                    course=course,
                )
                course.lessons.add(lesson)
                self.stdout.write(self.style.SUCCESS(f'Lesson {lesson_name} for {course_info["name"]} created'))

                # Create payments for each lesson
                for _ in range(random.randint(5, 10)):
                    user_id = random.randint(3, 4)
                    payment = Payment.objects.create(
                        user_id=user_id,
                        payment_date=timezone.now(),
                        paid_course=course,
                        paid_lesson=lesson,
                        payment_amount=random.uniform(10, 100),
                        payment_method=random.choice(['Наличные', 'Перевод на счет'])
                    )
                    self.stdout.write(self.style.SUCCESS(f'Payment for {lesson_name} of {course_info["name"]} created'))

            # Create course subscriptions
            for _ in range(random.randint(1, 3)):
                user_id = random.randint(3, 4)
                try:
                    subscription = CourseSubscription.objects.create(
                        user_id=user_id,
                        course=course,
                        is_active=True,
                        subscribed_at=timezone.now()
                    )
                    self.stdout.write(self.style.SUCCESS(f'Subscription created for Course {course_info["name"]} and User {user_id}'))
                except Exception:
                    self.stdout.write(self.style.ERROR(f'Subscription failed for Course {course_info["name"]} and User {user_id}'))

        self.stdout.write(self.style.SUCCESS('Data population completed successfully!'))
