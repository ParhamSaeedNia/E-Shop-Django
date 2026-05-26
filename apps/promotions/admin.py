from django.contrib import admin

from apps.promotions.models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "used_count",
        "max_uses",
        "is_active",
        "valid_until",
    )
    list_filter = ("discount_type", "is_active")
    search_fields = ("code", "description")


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "order", "discount_amount", "created_at")
    search_fields = ("coupon__code", "user__username")
