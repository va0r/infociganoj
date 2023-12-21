from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from payment.models import Payment, PaymentMethod
from payment.views import PaymentCreateAPIView
from users.models import User


class PaymentCreateAPIViewTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('payment.views.PaymentService')
    def test_create_cash_payment(self, mock_payment_service):
        # Arrange
        user = User.objects.create(email='test@example.com')
        request_data = {
            "payment_method": PaymentMethod.CASH.name,
            "payment_amount": 100
        }
        request = self.factory.post('/payment/', request_data)
        force_authenticate(request, user=user)

        mock_stripe_handler = MagicMock()
        mock_stripe_handler.create_and_save_payment.return_value = Payment(
            id=1,
            payment_method=PaymentMethod.CASH.name,
            payment_amount=100
        )
        mock_payment_service.return_value = mock_stripe_handler

        # Act
        view = PaymentCreateAPIView.as_view()
        response = view(request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['payment_method'], PaymentMethod.CASH.name)
        self.assertEqual(response.data['payment_amount'], 100)

    @patch('payment.views.PaymentService')
    def test_create_bank_transfer_payment(self, mock_payment_service):
        # Arrange
        user = User.objects.create(email='test@example.com')
        request_data = {
            "payment_method": PaymentMethod.BANK_TRANSFER.name,
            "payment_amount": 200
        }
        request = self.factory.post('/payment/', request_data)
        force_authenticate(request, user=user)

        mock_stripe_handler = MagicMock()
        mock_stripe_handler.create_and_save_payment.return_value = Payment(
            id=2,
            payment_method=PaymentMethod.BANK_TRANSFER.name,
            payment_amount=200,
            stripe_id='stripe123'
        )
        mock_payment_service.return_value = mock_stripe_handler

        # Act
        view = PaymentCreateAPIView.as_view()
        response = view(request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], 2)
        self.assertEqual(response.data['payment_method'], PaymentMethod.BANK_TRANSFER.name)
        self.assertEqual(response.data['payment_amount'], 200)
        self.assertEqual(response.data['stripe_id'], 'stripe123')

    ## =================================================================================================

    @patch('payment.views.PaymentService')
    def test_create_invalid_payment_method(self, mock_payment_service):
        # Arrange
        user = User.objects.create(email='test@example.com')
        request_data = {
            "payment_method": "unknown_method",
            "payment_amount": 100
        }
        request = self.factory.post('/payment/', request_data)
        force_authenticate(request, user=user)

        mock_stripe_handler = MagicMock()
        mock_stripe_handler.create_and_save_payment.return_value = Payment(
            id=1,
            payment_method="unknown_method",
            payment_amount=100
        )
        mock_payment_service.return_value = mock_stripe_handler

        # Act
        view = PaymentCreateAPIView.as_view()
        response = view(request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('payment_method', response.data)
        self.assertEqual(str(response.data['payment_method'][0]),
                         'Значения unknown_method нет среди допустимых вариантов.')
