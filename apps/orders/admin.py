from django.contrib import admin

from apps.orders.models import Order, OrderItem, UserLibrary


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_title", "unit_price", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "total",
        "coupon_code",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "user__username", "user__email")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(UserLibrary)
class UserLibraryAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "order", "download_count", "created_at")
    search_fields = ("user__username", "product__title")
