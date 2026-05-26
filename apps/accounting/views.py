from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.views.generic import TemplateView

from apps.accounting.models import Transaction
from apps.core.mixins import AdminRequiredMixin
from apps.orders.models import Order
from apps.promotions.models import Coupon


class AccountingDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "accounting/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        completed_orders = Order.objects.filter(status="completed")
        total_revenue = completed_orders.aggregate(total=Sum("total"))["total"] or Decimal("0")
        month_revenue = (
            completed_orders.filter(paid_at__gte=month_start).aggregate(total=Sum("total"))["total"]
            or Decimal("0")
        )
        total_orders = completed_orders.count()
        month_orders = completed_orders.filter(paid_at__gte=month_start).count()

        context["total_revenue"] = total_revenue
        context["month_revenue"] = month_revenue
        context["total_orders"] = total_orders
        context["month_orders"] = month_orders
        context["avg_order_value"] = (
            total_revenue / total_orders if total_orders else Decimal("0")
        )
        context["recent_transactions"] = Transaction.objects.select_related("user", "order")[:20]
        context["monthly_revenue"] = (
            completed_orders.annotate(month=TruncMonth("paid_at"))
            .values("month")
            .annotate(revenue=Sum("total"), count=Count("id"))
            .order_by("-month")[:6]
        )
        context["top_coupons"] = Coupon.objects.filter(used_count__gt=0).order_by("-used_count")[:5]
        context["recent_orders"] = completed_orders.select_related("user")[:10]
        return context
