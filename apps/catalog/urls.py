from django.urls import path

from apps.catalog import views

app_name = "catalog"

urlpatterns = [
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path("category/<slug:slug>/", views.ProductListView.as_view(), name="category"),
    path("products/", views.ProductListView.as_view(), name="products"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
