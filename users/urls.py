from django.urls import path
from .views import (
    Dashboard,
    RegisterView,
    ProfileView,
    ProfileUpdateView,
    OtpLoginView,
    SkillCreateView,
    ExperienceCreateView,
    PortfolioCreateView,
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", Dashboard.as_view(), name='home'),
    path("login/", OtpLoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(next_page='login'), name='logout'),
    path("signup/", RegisterView.as_view(), name='signup'),
    path("profile/", ProfileView.as_view(), name='profile'),
    path("profile/update/", ProfileUpdateView.as_view(), name='profile_update'),
    path("profile/skills/add/", SkillCreateView.as_view(), name="profile_skill_add"),
    path("profile/experience/add/", ExperienceCreateView.as_view(), name="profile_experience_add"),
    path("profile/portfolio/add/", PortfolioCreateView.as_view(), name="profile_portfolio_add"),
]
