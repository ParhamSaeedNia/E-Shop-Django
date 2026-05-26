from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.cart.models import CartItem
from apps.cart.services import get_or_create_cart
from apps.catalog.models import DigitalAsset
from apps.orders.models import Order, UserLibrary
from apps.orders.services import CheckoutService
from apps.promotions.forms import CheckoutForm
from apps.promotions.models import Coupon


def cart_detail(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related("product")
    subtotal = cart.subtotal

    coupon_discount = 0
    coupon_code = request.session.get("coupon_code", "")
    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
        if coupon and coupon.is_valid():
            coupon_discount = coupon.calculate_discount(subtotal)

    cart_total = max(subtotal - coupon_discount, 0)

    context = {
        "cart": cart,
        "items": items,
        "subtotal": subtotal,
        "coupon_code": coupon_code,
        "coupon_discount": coupon_discount,
        "cart_total": cart_total,
    }
    return render(request, "cart/cart.html", context)


@require_POST
def add_to_cart(request, product_id):
    from apps.catalog.models import Product

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save(update_fields=["quantity"])
    messages.success(request, f'"{product.title}" added to cart.')
    next_url = request.POST.get("next", "cart:detail")
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("cart:detail")


@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    action = request.POST.get("action")
    if action == "increment":
        item.quantity += 1
        item.save(update_fields=["quantity"])
    elif action == "decrement":
        if item.quantity > 1:
            item.quantity -= 1
            item.save(update_fields=["quantity"])
        else:
            item.delete()
    elif action == "remove":
        item.delete()
        messages.info(request, "Item removed from cart.")
    return redirect("cart:detail")


@require_POST
def apply_coupon(request):
    code = request.POST.get("coupon_code", "").strip()
    if not code:
        messages.error(request, "Please enter a coupon code.")
        return redirect("cart:detail")

    coupon = Coupon.objects.filter(code__iexact=code).first()
    if not coupon or not coupon.is_valid():
        messages.error(request, "Invalid or expired coupon code.")
        return redirect("cart:detail")

    request.session["coupon_code"] = coupon.code.upper()
    messages.success(request, f'Coupon "{coupon.code}" applied!')
    return redirect("cart:detail")


@require_POST
def remove_coupon(request):
    request.session.pop("coupon_code", None)
    messages.info(request, "Coupon removed.")
    return redirect("cart:detail")


@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    items = list(cart.items.select_related("product"))
    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect("catalog:products")

    subtotal = cart.subtotal
    coupon_code = request.session.get("coupon_code", "")
    coupon_discount = 0
    coupon = None
    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
        if coupon and coupon.is_valid():
            coupon_discount = coupon.calculate_discount(subtotal)

    referral_credit = request.user.profile.referral_credit
    max_credit_usable = max(subtotal - coupon_discount, 0)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = CheckoutService.process_order(
                    user=request.user,
                    cart=cart,
                    coupon_code=form.cleaned_data.get("coupon_code") or coupon_code,
                    use_referral_credit=form.cleaned_data.get("use_referral_credit", False),
                )
                request.session.pop("coupon_code", None)
                messages.success(request, f"Order {order.order_number} completed successfully!")
                return redirect("orders:detail", order_number=order.order_number)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = CheckoutForm(initial={"coupon_code": coupon_code})

    context = {
        "cart": cart,
        "items": items,
        "subtotal": subtotal,
        "coupon_discount": coupon_discount,
        "coupon_code": coupon_code,
        "referral_credit": referral_credit,
        "max_credit_usable": min(referral_credit, max_credit_usable),
        "total": max(subtotal - coupon_discount, 0),
        "form": form,
    }
    return render(request, "cart/checkout.html", context)


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        order_number=order_number,
        user=request.user,
    )
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def download_asset(request, asset_id):
    asset = get_object_or_404(DigitalAsset, pk=asset_id)
    has_access = UserLibrary.objects.filter(
        user=request.user, product=asset.product
    ).exists()
    if not has_access and not request.user.is_staff:
        raise Http404

    library_item = UserLibrary.objects.filter(
        user=request.user, product=asset.product
    ).first()
    if library_item:
        library_item.download_count += 1
        library_item.last_downloaded_at = timezone.now()
        library_item.save(update_fields=["download_count", "last_downloaded_at"])

    asset.product.download_count += 1
    asset.product.save(update_fields=["download_count"])

    return FileResponse(asset.file.open("rb"), as_attachment=True, filename=asset.file.name.split("/")[-1])
