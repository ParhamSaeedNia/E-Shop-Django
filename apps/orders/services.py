from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction

from apps.accounting.models import Transaction
from apps.accounts.models import ReferralReward
from apps.cart.models import Cart
from apps.orders.models import Order, OrderItem, UserLibrary
from apps.promotions.models import Coupon, CouponUsage


REFERRAL_REWARD_PERCENT = Decimal("5")


class CheckoutService:
    @staticmethod
    @transaction.atomic
    def process_order(user, cart, coupon_code=None, use_referral_credit=False):
        items = list(cart.items.select_related("product"))
        if not items:
            raise ValueError("Cart is empty")

        subtotal = sum(item.line_total for item in items)
        discount_amount = Decimal("0")
        coupon = None
        referral_credit_used = Decimal("0")

        if coupon_code:
            coupon = Coupon.objects.filter(code__iexact=coupon_code.strip()).first()
            if not coupon or not coupon.is_valid():
                raise ValueError("Invalid or expired coupon code")
            user_usage = CouponUsage.objects.filter(coupon=coupon, user=user).count()
            if user_usage >= coupon.max_uses_per_user:
                raise ValueError("Coupon usage limit reached for this account")
            discount_amount = coupon.calculate_discount(subtotal)

        profile = user.profile
        if use_referral_credit and profile.referral_credit > 0:
            referral_credit_used = min(profile.referral_credit, subtotal - discount_amount)

        total = max(subtotal - discount_amount - referral_credit_used, Decimal("0"))

        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            discount_amount=discount_amount,
            referral_credit_used=referral_credit_used,
            total=total,
            coupon=coupon,
            coupon_code=coupon.code if coupon else "",
            status="paid",
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_title=item.product.title,
                unit_price=item.product.price,
                quantity=item.quantity,
                line_total=item.line_total,
            )
            UserLibrary.objects.get_or_create(
                user=user,
                product=item.product,
                order=order,
            )

        if coupon:
            CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                order=order,
                discount_amount=discount_amount,
            )
            coupon.used_count += 1
            coupon.save(update_fields=["used_count"])

        if referral_credit_used > 0:
            profile.referral_credit -= referral_credit_used
            profile.save(update_fields=["referral_credit"])

        Transaction.objects.create(
            order=order,
            user=user,
            transaction_type="sale",
            amount=total,
            description=f"Order {order.order_number}",
        )

        CheckoutService._process_referral_reward(user, order, total)
        cart.items.all().delete()

        from django.utils import timezone

        order.paid_at = timezone.now()
        order.status = "completed"
        order.save(update_fields=["paid_at", "status"])

        return order

    @staticmethod
    def _process_referral_reward(user, order, total):
        profile = user.profile
        if not profile.referred_by:
            return

        reward_amount = (total * REFERRAL_REWARD_PERCENT / Decimal("100")).quantize(
            Decimal("0.01")
        )
        if reward_amount <= 0:
            return

        ReferralReward.objects.create(
            referrer=profile.referred_by,
            referred_user=user,
            order=order,
            amount=reward_amount,
            status="credited",
        )
        referrer_profile = profile.referred_by.profile
        referrer_profile.referral_credit += reward_amount
        referrer_profile.save(update_fields=["referral_credit"])

        Transaction.objects.create(
            order=order,
            user=profile.referred_by,
            transaction_type="referral_payout",
            amount=reward_amount,
            description=f"Referral reward from {user.username} order {order.order_number}",
        )
