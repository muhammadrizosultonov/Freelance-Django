from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Skill, Experience, PortfolioItem


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class PortfolioInline(admin.TabularInline):
    model = PortfolioItem
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "first_name", "last_name", "role", "email", "phone", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email", "phone")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Profil",
            {
                "fields": (
                    "role",
                    "bio",
                    "avatar",
                    "cover_photo",
                    "phone",
                    "title",
                    "location",
                    "website",
                    "telegram",
                    "hourly_rate",
                    "is_verified",
                    "is_online",
                    "categories",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profil", {"fields": ("role", "bio", "avatar", "phone")}),
    )
    inlines = [SkillInline, ExperienceInline, PortfolioInline]
    filter_horizontal = ("groups", "user_permissions", "categories")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)
