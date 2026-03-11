from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignupForm(UserCreationForm):

    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=CustomUser.Role.choices)

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email", "role", "password1", "password2")


    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon mavjud")
        return email