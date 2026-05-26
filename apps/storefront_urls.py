from django.urls import path

from apps.catalog.views import HomeView

app_name = "storefront"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
