from django.contrib import admin

from apps.catalog.models import Category, DigitalAsset, Product


class DigitalAssetInline(admin.TabularInline):
    model = DigitalAsset
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "sort_order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "price",
        "compare_at_price",
        "is_active",
        "is_featured",
    )
    list_filter = ("category", "is_active", "is_featured")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "description")
    inlines = [DigitalAssetInline]


@admin.register(DigitalAsset)
class DigitalAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "file_type", "file_size", "sort_order")
    list_filter = ("file_type",)
