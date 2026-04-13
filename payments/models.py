from django.db import models

# Create your models here.


import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending",   "Pending"),
        ("success",   "Success"),
        ("failed",    "Failed"),
        ("abandoned", "Abandoned"),
    ]

    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    reference     = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    email         = models.EmailField()
    amount        = models.PositiveIntegerField(help_text="Amount in kobo")
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    channel       = models.CharField(max_length=50, blank=True)
    currency      = models.CharField(max_length=10, default="NGN")
    paid_at       = models.DateTimeField(null=True, blank=True)
    metadata      = models.JSONField(default=dict, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.status}"

    @property
    def amount_naira(self):
        return self.amount / 100