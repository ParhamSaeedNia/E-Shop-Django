from django.urls import path

from apps.cart import views as cart_views

app_name = "orders"

urlpatterns = [
    path("", cart_views.order_list, name="list"),
    path("<str:order_number>/", cart_views.order_detail, name="detail"),
    path("download/<int:asset_id>/", cart_views.download_asset, name="download"),
]
