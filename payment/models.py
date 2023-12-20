from enum import Enum

from django.db import models

from constants import NULLABLE


class PaymentMethod(Enum):
    CASH = 'Наличные'
    BANK_TRANSFER = 'Перевод на счет'


class Payment(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='user', related_name="payments")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='payment_date', **NULLABLE)
    paid_course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, verbose_name='paid_course', **NULLABLE)
    paid_lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, verbose_name='paid_lesson', **NULLABLE)
    payment_amount = models.IntegerField(verbose_name='payment_amount')
    payment_method = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in PaymentMethod])
    stripe_id = models.CharField(max_length=300, verbose_name='stripe_id', **NULLABLE)

    def __str__(self):
        return f'{self.user}: {self.payment_amount}'

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
