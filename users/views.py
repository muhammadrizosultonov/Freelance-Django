from django.shortcuts import render, redirect
from django.db.models import Sum, Avg, Count, Q
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import SignupForm, SkillForm, ExperienceForm, PortfolioItemForm, OtpSendForm, OtpVerifyForm, OtpPasswordForm, otp_context
from .models import CustomUser
from service.models import Project, Bid, Contract, Review
from chat.models import Message
# Create your views here.


class Dashboard(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        unread_messages = Message.objects.filter(Q(conversation__user1=request.user) | Q(conversation__user2=request.user), is_read=False,).exclude(sender=request.user).count()
        if request.user.role == CustomUser.Role.FREELANCER:
            proposals_qs = (Bid.objects.filter(freelancer=request.user).select_related("project", "project__client").order_by("-created_at"))
            active_contracts = (Contract.objects.filter(freelancer=request.user, status=Contract.StatusChoices.ACTIVE).select_related("project").order_by("-created_at"))
            completed_contracts = Contract.objects.filter(freelancer=request.user, status=Contract.StatusChoices.FINISHED)
            total_earnings = completed_contracts.aggregate(total=Sum("agreed_price")).get("total") or 0
            reviews_agg = Review.objects.filter(freelancer=request.user).aggregate(avg_rating=Avg("rating"), total_reviews=Count("id"))
            avg_rating = reviews_agg.get("avg_rating") or 0
            reviews_count = reviews_agg.get("total_reviews") or 0
            profile_fields = [
                request.user.first_name,
                request.user.last_name,
                request.user.email,
                request.user.bio,
                request.user.avatar,
            ]
            filled = sum(1 for value in profile_fields if value)
            profile_completion = int((filled / len(profile_fields)) * 100)
            context = {
                "proposals": proposals_qs[:5],
                "proposals_count": proposals_qs.count(),
                "active_proposals": proposals_qs.filter(status=Bid.StatusChoices.PENDING).count(),
                "active_jobs_list": [c.project for c in active_contracts],
                "active_jobs": active_contracts.count(),
                "completed_jobs": completed_contracts.count(),
                "finished_contracts_count": completed_contracts.count(),
                "total_earnings": int(total_earnings),
                "rating": round(float(avg_rating), 1) if avg_rating else 0,
                "reviews_count": reviews_count,
                "profile_completion": profile_completion,
                "unread_messages": unread_messages,
            }
            return render(request, 'freelancer_dashboard.html', context)
        if request.user.role == CustomUser.Role.CLIENT:

            projects_qs = (Project.objects.filter(client=request.user).order_by('-created_at').prefetch_related("contract_set", "contract_set__freelancer"))
            active_projects_qs = projects_qs.exclude(status__in=[Project.StatusChoices.COMPLETED, Project.StatusChoices.CANCELLED])
            contracts_qs = Contract.objects.filter(client=request.user).exclude(status=Contract.StatusChoices.CANCELLED)
            total_spent = contracts_qs.aggregate(total=Sum("agreed_price")).get("total") or 0
            bids_qs = Bid.objects.filter(project__client=request.user).select_related("project", "freelancer")
            pending_proposals = bids_qs.filter(status=Bid.StatusChoices.PENDING).count()
            recent_proposals = bids_qs.order_by("-created_at")[:5]
            
            context = {
                "active_projects": active_projects_qs,
                "projects_count": projects_qs.count(),
                "total_projects": projects_qs.count(),
                "completed_projects": projects_qs.filter(status=Project.StatusChoices.COMPLETED).count(),
                "active_projects_count": active_projects_qs.count(),
                "pending_proposals": pending_proposals,
                "total_spent": int(total_spent),
                "recent_proposals": recent_proposals,
                "proposals_count": bids_qs.count(),
                "contracts_count": contracts_qs.count(),
                "unread_messages": unread_messages,
            }
            return render(request, 'client_dashboard.html', context)
        return redirect("home")


class RegisterView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, 'signup.html', {"form": form})
    
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        return render(request, "signup.html", {"form": form})


class OtpLoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name, otp_context(request))

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home")

        action = request.POST.get("action")
        if action == "send":
            form = OtpSendForm(request, request.POST)
            if form.is_valid():
                form.save()
            return render(request, self.template_name, otp_context(request, form=form))

        if action == "verify":
            form = OtpVerifyForm(request, request.POST)
            if form.is_valid():
                form.save()
            return render(request, self.template_name, otp_context(request, form=form))

        if action == "password":
            form = OtpPasswordForm(request, request.POST)
            if form.is_valid():
                form.login_user()
                return redirect("home")
            return render(request, self.template_name, otp_context(request, form=form))

        context = otp_context(request)
        context["error"] = "Noto'g'ri amal."
        return render(request, self.template_name, context)



class ProfileView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        profile_user = request.user
        if profile_user.role == CustomUser.Role.FREELANCER:
            contracts = Contract.objects.filter(freelancer=profile_user)
            completed_contracts = contracts.filter(status=Contract.StatusChoices.FINISHED)
            total_earned = completed_contracts.aggregate(total=Sum("agreed_price")).get("total") or 0
            reviews_agg = Review.objects.filter(freelancer=profile_user).aggregate(avg_rating=Avg("rating"), total_reviews=Count("id"))
            avg_rating = reviews_agg.get("avg_rating") or 0
            reviews_count = reviews_agg.get("total_reviews") or 0
            success_rate = int((completed_contracts.count() / contracts.count()) * 100) if contracts.exists() else 0
            completed_jobs = completed_contracts.count()
        else:
            projects = Project.objects.filter(client=profile_user)
            completed_projects = projects.filter(status=Project.StatusChoices.COMPLETED).count()
            contracts = Contract.objects.filter(client=profile_user)
            total_spent = contracts.aggregate(total=Sum("agreed_price")).get("total") or 0
            avg_rating = 0
            reviews_count = 0
            success_rate = int((completed_projects / projects.count()) * 100) if projects.exists() else 0
            completed_jobs = completed_projects
            total_earned = total_spent

        context = {
            'profile_user': profile_user,
            'is_own_profile': True,
            'completed_jobs': completed_jobs,
            'success_rate': success_rate,
            'response_time': 0,
            'total_earned': int(total_earned),
            'rating': round(float(avg_rating), 1) if avg_rating else 0,
            'reviews_count': reviews_count,
            'skill_form': SkillForm(),
            'experience_form': ExperienceForm(),
            'portfolio_form': PortfolioItemForm(),
        }
        return render(request, 'profile.html', context)


class SkillCreateView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, "Ko'nikma qo'shildi.")
        else:
            messages.error(request, "Ko'nikma qo'shishda xatolik.")
        return redirect('profile')


class ExperienceCreateView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            messages.success(request, "Tajriba qo'shildi.")
        else:
            messages.error(request, "Tajriba qo'shishda xatolik.")
        return redirect('profile')


class PortfolioCreateView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        form = PortfolioItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, "Portfolio qo'shildi.")
        else:
            messages.error(request, "Portfolio qo'shishda xatolik.")
        return redirect('profile')


class ProfileUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        request.user.bio = request.POST.get('bio', '').strip()
        request.user.save(update_fields=['bio', 'updated_at'])
        return redirect('profile')
