from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Transaction(TimeStampedModel):
    TYPE_CHOICES = [
        ("sale", "Sale"),
        ("refund", "Refund"),
        ("referral_payout", "Referral Payout"),
        ("adjustment", "Adjustment"),
    ]

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_transactions",
    )

    class Meta:
        db_table = "accounting_transaction"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type}: ${self.amount}"
