from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import mock

from courses.models.course import Course
from payment.models import Payment, PaymentMethod
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentRetrieveAPIViewTestCase(APITestCase):
    def setUp(self, null=None):
        self.user = User.objects.create(email='test@example.com', phone='123456789', city='Test City')
        self.course_data = {'name': 'Test Course', 'description': 'Test Description'}
        self.course = Course.objects.create(**self.course_data)
        self.user_payment = Payment.objects.create(
            user=self.user,
            payment_date='2023-01-01T00:00:00Z',
            paid_course=self.course,
            paid_lesson=null,
            payment_amount=100,
            payment_method=PaymentMethod.CASH.name,
            stripe_id='stripe123'
        )
        self.url = reverse('payment:payment-retrieve', kwargs={'pk': self.user_payment.pk})
        self.client.force_authenticate(user=self.user)  # Авторизация пользователя

    @patch('stripe.PaymentIntent.retrieve')
    def test_retrieve_payment_with_valid_pk(self, mock_retrieve):
        # Задаем фиктивный ответ от Stripe API
        mock_retrieve.return_value = {
            'id': 'stripe123',
            'status': 'succeeded',
            # Другие необходимые поля, которые вы хотите проверить
        }

        response = self.client.get(self.url)

        # Проверки результата запроса
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], 'succeeded')

        # Проверяем, что mock_retrieve был вызван один раз с нужными параметрами
        mock_retrieve.assert_called_once_with('stripe123')

    @patch('stripe.PaymentIntent.retrieve')
    def test_retrieve_payment_with_none_stripe_id(self, mock_retrieve):
        # Задаем, что stripe_id равен None
        self.user_payment.stripe_id = None
        self.user_payment.save()

        response = self.client.get(self.url)

        # Проверки результата запроса
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Для этого платежа не существует Stripe ID.')

        # Проверяем, что mock_retrieve не был вызван
        mock_retrieve.assert_not_called()

    def test_retrieve_nonexistent_payment(self):
        # Устанавливаем несуществующий pk
        non_existent_pk = 999
        self.url = reverse('payment:payment-retrieve', kwargs={'pk': non_existent_pk})

        response = self.client.get(self.url)

        # Проверки результата запроса
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(str(response.data['error']), 'Произошла ошибка: No Payment matches the given query.')
