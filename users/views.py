from django.shortcuts import render
from django.views import View
# Create your views here.


class Dashboard(View):
    def get(self, request):
        return render(request, 'freelancer_dashboard.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'signup.html')