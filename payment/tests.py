from django.test import TestCase

from payment.models import Payment, PaymentMethod
from users.models import User


class PaymentStrMethodTest(TestCase):

    def setUp(self):
        # Create a User instance first
        self.user = User.objects.create(email='test@example.com', phone='123456789', city='Test City')

        # Then create the Payment instance
        self.user_payment = Payment(
            user=self.user,
            payment_date='2023-01-01T00:00:00Z',
            paid_course_id=1,
            paid_lesson_id=2,
            payment_amount=100,
            payment_method=PaymentMethod.CASH.name,
            stripe_id='stripe123'
        )

    def test_str_method_returns(self):
        expected_str = 'test@example.com: 100'
        self.assertEqual(str(self.user_payment), expected_str)
