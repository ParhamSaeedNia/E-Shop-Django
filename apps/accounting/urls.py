from django.urls import path

from apps.accounting import views

app_name = "accounting"

urlpatterns = [
    path("", views.AccountingDashboardView.as_view(), name="dashboard"),
]
