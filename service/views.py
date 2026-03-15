from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse
from .forms import ProjectCreateForm, BidCreateForm, FreelancerSettingsForm, ClientSettingsForm, ReviewForm
from .models import Project, Bid, Contract, Review
from chat.models import Conversation
from users.models import CustomUser

# Create your views here.


class ProjectCreateView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = ProjectCreateForm()
        return render(request, "project_create.html", {"form": form})

    def post(self, request):
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.status = Project.StatusChoices.OPEN
            project.save()
            return redirect("home")
        return render(request, "project_create.html", {"form": form})


class ProjectListView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.FREELANCER:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        projects = (
            Project.objects.filter(status=Project.StatusChoices.OPEN)
            .select_related("client")
            .order_by("-created_at")
        )
        bid_project_ids = set(
            Bid.objects.filter(freelancer=request.user, project__in=projects).values_list("project_id", flat=True)
        )
        context = {
            "projects": projects,
            "bid_project_ids": bid_project_ids,
        }
        return render(request, "project_list.html", context)


class BidCreateView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.FREELANCER:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if project.status != Project.StatusChoices.OPEN:
            messages.error(request, "Bu loyiha hozirda yangi arizalarni qabul qilmaydi.")
            return redirect("project_list")

        existing = Bid.objects.filter(project=project, freelancer=request.user).first()
        if existing:
            messages.info(request, "Siz bu loyihaga allaqachon ariza yuborgansiz.")
            return redirect("project_list")
        form = BidCreateForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.project = project
            bid.freelancer = request.user
            bid.status = Bid.StatusChoices.PENDING
            bid.save()
            messages.success(request, "Ariza yuborildi.")
            return redirect("project_list")

        messages.error(request, "Ariza yuborishda xatolik. Iltimos, maydonlarni tekshiring.")
        return redirect("project_list")


class FreelancerProposalsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.FREELANCER:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        status = request.GET.get("status", "").lower()
        status_map = {
            "pending": Bid.StatusChoices.PENDING,
            "accepted": Bid.StatusChoices.ACCEPTED,
            "rejected": Bid.StatusChoices.REJECTED,
        }
        qs = Bid.objects.filter(freelancer=request.user).select_related("project", "project__client")
        if status in status_map:
            qs = qs.filter(status=status_map[status])
        qs = qs.order_by("-created_at")

        context = {
            "proposals": qs,
            "active_filter": status,
            "count_all": Bid.objects.filter(freelancer=request.user).count(),
            "count_pending": Bid.objects.filter(
                freelancer=request.user, status=Bid.StatusChoices.PENDING
            ).count(),
            "count_accepted": Bid.objects.filter(
                freelancer=request.user, status=Bid.StatusChoices.ACCEPTED
            ).count(),
            "count_rejected": Bid.objects.filter(
                freelancer=request.user, status=Bid.StatusChoices.REJECTED
            ).count(),
        }
        return render(request, "freelancer_proposals.html", context)


class FreelancerActiveJobsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.FREELANCER:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        contracts = (
            Contract.objects.filter(freelancer=request.user, status=Contract.StatusChoices.ACTIVE)
            .select_related("project", "client")
            .order_by("-created_at")
        )
        return render(request, "freelancer_active_jobs.html", {"contracts": contracts})


class FreelancerEarningsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.FREELANCER:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        finished = (
            Contract.objects.filter(freelancer=request.user, status=Contract.StatusChoices.FINISHED)
            .select_related("project", "client")
            .order_by("-created_at")
        )
        total_earnings = finished.aggregate(total=Sum("agreed_price")).get("total") or 0
        context = {"contracts": finished, "total_earnings": int(total_earnings)}
        return render(request, "freelancer_earnings.html", context)


class FreelancerPaymentsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.FREELANCER:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        payments = (
            Contract.objects.filter(freelancer=request.user, status=Contract.StatusChoices.FINISHED)
            .select_related("project", "client")
            .order_by("-created_at")
        )
        return render(request, "freelancer_payments.html", {"payments": payments})


class FreelancerWithdrawView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.FREELANCER:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, "freelancer_withdraw.html")

    def post(self, request):
        messages.success(request, "Pul yechish so'rovi yuborildi.")
        return redirect("freelancer_withdraw")


class FreelancerSettingsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.FREELANCER:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = FreelancerSettingsForm(instance=request.user)
        return render(request, "freelancer_settings.html", {"form": form})

    def post(self, request):
        form = FreelancerSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Sozlamalar saqlandi.")
            return redirect("freelancer_settings")
        return render(request, "freelancer_settings.html", {"form": form})


class ClientProjectsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        projects = (
            Project.objects.filter(client=request.user)
            .order_by("-created_at")
            .prefetch_related("contract_set", "contract_set__freelancer")
        )
        return render(request, "client_projects.html", {"projects": projects})


class ClientProposalsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        status = request.GET.get("status", "").lower()
        status_map = {
            "pending": Bid.StatusChoices.PENDING,
            "accepted": Bid.StatusChoices.ACCEPTED,
            "rejected": Bid.StatusChoices.REJECTED,
        }
        qs = Bid.objects.filter(project__client=request.user).select_related("project", "freelancer")
        if status in status_map:
            qs = qs.filter(status=status_map[status])
        qs = qs.order_by("-created_at")
        context = {
            "proposals": qs,
            "active_filter": status,
            "count_all": Bid.objects.filter(project__client=request.user).count(),
            "count_pending": Bid.objects.filter(
                project__client=request.user, status=Bid.StatusChoices.PENDING
            ).count(),
            "count_accepted": Bid.objects.filter(
                project__client=request.user, status=Bid.StatusChoices.ACCEPTED
            ).count(),
            "count_rejected": Bid.objects.filter(
                project__client=request.user, status=Bid.StatusChoices.REJECTED
            ).count(),
        }
        return render(request, "client_proposals.html", context)


class ClientPaymentsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        payments = (
            Contract.objects.filter(client=request.user)
            .select_related("project", "freelancer")
            .order_by("-created_at")
        )
        return render(request, "client_payments.html", {"payments": payments})


class ClientReportsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        projects = Project.objects.filter(client=request.user)
        active_projects = projects.exclude(
            status__in=[Project.StatusChoices.COMPLETED, Project.StatusChoices.CANCELLED]
        )
        contracts = Contract.objects.filter(client=request.user).exclude(
            status=Contract.StatusChoices.CANCELLED
        )
        total_spent = contracts.aggregate(total=Sum("agreed_price")).get("total") or 0
        context = {
            "total_projects": projects.count(),
            "active_projects": active_projects.count(),
            "completed_projects": projects.filter(status=Project.StatusChoices.COMPLETED).count(),
            "pending_proposals": Bid.objects.filter(
                project__client=request.user, status=Bid.StatusChoices.PENDING
            ).count(),
            "total_spent": int(total_spent),
        }
        return render(request, "client_reports.html", context)


class ClientSettingsView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = ClientSettingsForm(instance=request.user)
        return render(request, "client_settings.html", {"form": form})

    def post(self, request):
        form = ClientSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Sozlamalar saqlandi.")
            return redirect("client_settings")
        return render(request, "client_settings.html", {"form": form})


class ClientReviewCreateView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, contract_id):
        contract = get_object_or_404(Contract, id=contract_id, client=request.user)
        if contract.status not in [Contract.StatusChoices.FINISHED, Contract.StatusChoices.CANCELLED]:
            messages.error(request, "Baholash faqat tugallangan yoki bekor qilingan shartnomalarda mumkin.")
            return redirect("client_payments")
        if hasattr(contract, "review"):
            messages.info(request, "Bu shartnoma uchun baho allaqachon berilgan.")
            return redirect("client_payments")
        form = ReviewForm()
        return render(request, "client_review_create.html", {"form": form, "contract": contract})

    def post(self, request, contract_id):
        contract = get_object_or_404(Contract, id=contract_id, client=request.user)
        if contract.status not in [Contract.StatusChoices.FINISHED, Contract.StatusChoices.CANCELLED]:
            messages.error(request, "Baholash faqat tugallangan yoki bekor qilingan shartnomalarda mumkin.")
            return redirect("client_payments")
        if hasattr(contract, "review"):
            messages.info(request, "Bu shartnoma uchun baho allaqachon berilgan.")
            return redirect("client_payments")
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.contract = contract
            review.client = request.user
            review.freelancer = contract.freelancer
            review.save()
            messages.success(request, "Baho saqlandi.")
            return redirect("client_payments")
        return render(request, "client_review_create.html", {"form": form, "contract": contract})


class ClientBidActionView(LoginRequiredMixin, View):
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, bid_id, action):
        bid = get_object_or_404(Bid, id=bid_id, project__client=request.user)
        if bid.status != Bid.StatusChoices.PENDING:
            messages.info(request, "Bu ariza allaqachon ko'rib chiqilgan.")
            return redirect("client_proposals")

        if action == "accept":
            active_contract = Contract.objects.filter(
                project=bid.project, status=Contract.StatusChoices.ACTIVE
            ).first()
            if active_contract:
                messages.error(request, "Bu loyiha bo'yicha faol shartnoma mavjud.")
                return redirect("client_proposals")
            bid.status = Bid.StatusChoices.ACCEPTED
            bid.save(update_fields=["status"])
            Bid.objects.filter(project=bid.project, status=Bid.StatusChoices.PENDING).exclude(
                id=bid.id
            ).update(status=Bid.StatusChoices.REJECTED)
            Contract.objects.create(
                project=bid.project,
                client=request.user,
                freelancer=bid.freelancer,
                agreed_price=bid.price,
                status=Contract.StatusChoices.ACTIVE,
            )
            bid.project.status = Project.StatusChoices.IN_PROGRESS
            bid.project.save(update_fields=["status"])
            Conversation.get_or_create_between(request.user, bid.freelancer)
            messages.success(request, "Ariza qabul qilindi va shartnoma yaratildi.")
            return redirect(f"{reverse('chat')}?user={bid.freelancer.id}")
        elif action == "reject":
            bid.status = Bid.StatusChoices.REJECTED
            bid.save(update_fields=["status"])
            messages.success(request, "Ariza rad etildi.")
        else:
            messages.error(request, "Noto'g'ri amal.")
        return redirect("client_proposals")
