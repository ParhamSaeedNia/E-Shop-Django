from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.accounts.forms import LoginForm, ProfileForm, RegisterForm
from apps.accounts.models import ReferralReward
from apps.cart.services import merge_session_cart
from apps.orders.models import Order, UserLibrary


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("storefront:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend="django.contrib.auth.backends.ModelBackend")
        merge_session_cart(self.request, self.object)
        messages.success(self.request, "Welcome! Your account has been created.")
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("storefront:home")
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        merge_session_cart(self.request, self.request.user)
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return response


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("storefront:home")


class DashboardView(TemplateView):
    template_name = "accounts/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["recent_orders"] = Order.objects.filter(user=user)[:5]
        context["library_count"] = UserLibrary.objects.filter(user=user).count()
        context["referral_count"] = ReferralReward.objects.filter(referrer=user).count()
        context["referral_credit"] = user.profile.referral_credit
        context["referral_code"] = user.profile.referral_code
        return context


class ProfileUpdateView(UpdateView):
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user.profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


class ReferralsView(TemplateView):
    template_name = "accounts/referrals.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = user.profile
        context["referral_code"] = profile.referral_code
        context["referral_credit"] = profile.referral_credit
        context["referrals"] = ReferralReward.objects.filter(referrer=user).select_related(
            "referred_user", "order"
        )
        context["referral_link"] = self.request.build_absolute_uri(
            f"/accounts/register/?ref={profile.referral_code}"
        )
        return context


class LibraryView(TemplateView):
    template_name = "accounts/library.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["library_items"] = (
            UserLibrary.objects.filter(user=self.request.user)
            .select_related("product", "order")
            .prefetch_related("product__assets")
        )
        return context
