from django.db import models
from registration.models import registeredUser


class Transaction(models.Model):
    user = models.ForeignKey(registeredUser, on_delete=models.CASCADE, related_name="transactions")
    txnid = models.CharField(max_length=100)
    amount = models.FloatField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.txnid} "
    
    
    
from django.db import models
from django.utils import timezone

class MasterClassPayment(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    designation = models.CharField(max_length=100, blank=True, null=True)
    institution_name = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    txnid = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=[('PENDING','PENDING'), ('SUCCESS','SUCCESS'), ('FAILED','FAILED')],
        default="PENDING"
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.full_name} - {self.status}"
