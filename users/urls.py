from django.urls import path
from .views import Dashboard, RegisterView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", Dashboard.as_view(), name='home'),
    path("login/", LoginView.as_view(template_name='login.html'), name='login'),
    path("logout/", LogoutView.as_view(next_page='login'), name='logout'),
    path("signup/", RegisterView.as_view(), name='signup')
]