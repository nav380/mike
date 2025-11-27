from django.urls import path
from .views import *
urlpatterns = [
    path("", payment_page, name="payment_page"),
    path("start/", start_payment, name="start_payment"),
    path("success/", payment_success, name="pay_success"),
    path("failure/", payment_failure, name="pay_failure"),
    path('payment_masterclass/',masterclass_payment,name="payment_masterclasss"),
    path('masterclass-payment-success/',masterclass_payment_success,name="masterclass-payment-success"),
    path('masterclass-payment-failure/',masterclass_payment_failure,name="masterclass-payment-failure"),
    path("pay_redirect/<str:txnid>/", pay_redirect, name="pay_redirect"),
]