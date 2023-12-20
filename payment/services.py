import os

import stripe
from rest_framework import status
from rest_framework.response import Response

from payment.models import PaymentMethod, Payment


class PaymentService:
    def __init__(self):
        self.stripe_api_key = os.getenv('STRIPE_SECRET_KEY')

    def create_payment(self, user, amount, payment_method):
        try:
            stripe.api_key = self.stripe_api_key
            if payment_method == PaymentMethod.BANK_TRANSFER.name:
                payment_intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency='usd',
                    payment_method_types=['card'],
                    description=f'Payment for user: {user}',
                )
                return payment_intent.id
            elif payment_method == PaymentMethod.CASH.name:
                payment = Payment.objects.create(
                    user=user,
                    payment_amount=amount,
                    payment_method=PaymentMethod.CASH,
                    description=f'Payment for user: {user}',
                )
                return payment.stripe_id
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create_and_save_payment(self, user, amount, payment_method):
        stripe_id = self.create_payment(user, amount, payment_method)
        if stripe_id is not None:
            payment = self.save_payment(user, amount, payment_method, stripe_id)
            return payment
        else:
            return None

    def save_payment(self, user, amount, payment_method, stripe_id):
        payment = Payment.objects.create(
            user=user,
            payment_amount=amount,
            payment_method=payment_method,
            stripe_id=stripe_id,
        )
        return payment

    @staticmethod
    def retrieve(stripe_id):
        return stripe.PaymentIntent.retrieve(stripe_id)


class PaymentError(Exception):
    pass
