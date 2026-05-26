import secrets
import string

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


def generate_referral_code():
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


class Profile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_referral_code,
        editable=False,
    )
    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals_made",
    )
    referral_credit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "accounts_profile"

    def __str__(self):
        return f"Profile({self.user.username})"


class ReferralReward(TimeStampedModel):
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_rewards",
    )
    referred_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_reward_source",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="referral_rewards",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("credited", "Credited"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )

    class Meta:
        db_table = "accounts_referral_reward"
        unique_together = [("referrer", "referred_user", "order")]

    def __str__(self):
        return f"ReferralReward({self.referrer.username}, ${self.amount})"
