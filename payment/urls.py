from django.urls import path

from payment.apps import PaymentConfig

from payment.views import PaymentListAPIView, PaymentCreateAPIView, PaymentRetrieveAPIView

app_name = PaymentConfig.name


urlpatterns = [
    path('', PaymentListAPIView.as_view(), name='payment-list'),
    path('create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('retrieve/<int:pk>/', PaymentRetrieveAPIView.as_view(), name='payment-retrieve')
   ]
