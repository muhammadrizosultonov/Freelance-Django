from django.contrib import admin
from .models import Project, Bid, Contract, Review


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "status", "budget", "deadline", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "description", "client__username", "client__email")
    date_hierarchy = "created_at"
    list_select_related = ("client",)


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("project", "freelancer", "price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("project__title", "freelancer__username", "freelancer__email")
    date_hierarchy = "created_at"
    list_select_related = ("project", "freelancer")


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("project", "client", "freelancer", "agreed_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("project__title", "client__username", "freelancer__username")
    date_hierarchy = "created_at"
    list_select_related = ("project", "client", "freelancer")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("contract", "client", "freelancer", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("contract__project__title", "client__username", "freelancer__username")
    list_select_related = ("contract", "client", "freelancer")
