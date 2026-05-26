from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from apps.accounts.models import Profile, ReferralReward


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    readonly_fields = ("referral_code", "referral_credit")
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "date_joined")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred_user", "amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("referrer__username", "referred_user__username")
