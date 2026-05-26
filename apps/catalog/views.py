from django.db.models import Q
from django.views.generic import DetailView, ListView

from apps.catalog.models import Category, Product


class HomeView(ListView):
    model = Product
    template_name = "storefront/home.html"
    context_object_name = "featured_products"

    def get_queryset(self):
        return Product.objects.filter(is_active=True, is_featured=True).select_related(
            "category"
        )[:8]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["latest_products"] = (
            Product.objects.filter(is_active=True).select_related("category")[:12]
        )
        return context


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category")
        category_slug = self.kwargs.get("slug")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(short_description__icontains=search)
            )
        sort = self.request.GET.get("sort", "newest")
        if sort == "price_low":
            qs = qs.order_by("price")
        elif sort == "price_high":
            qs = qs.order_by("-price")
        elif sort == "title":
            qs = qs.order_by("title")
        else:
            qs = qs.order_by("-created_at")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        slug = self.kwargs.get("slug")
        if slug:
            context["current_category"] = Category.objects.filter(slug=slug).first()
        context["search_query"] = self.request.GET.get("q", "")
        context["current_sort"] = self.request.GET.get("sort", "newest")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category").prefetch_related(
            "assets"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_products"] = (
            Product.objects.filter(
                category=self.object.category, is_active=True
            )
            .exclude(pk=self.object.pk)[:4]
        )
        return context


class CategoryListView(ListView):
    model = Category
    template_name = "catalog/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(is_active=True)
