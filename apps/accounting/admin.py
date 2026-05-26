from django.contrib import admin

from apps.accounting.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_type",
        "amount",
        "user",
        "order",
        "description",
        "created_at",
    )
    list_filter = ("transaction_type", "created_at")
    search_fields = ("description", "user__username", "order__order_number")
    readonly_fields = ("created_at", "updated_at")
