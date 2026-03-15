from django import forms
from django.utils import timezone
from .models import Project, Bid, Review
from users.models import CustomUser, Category


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "category", "budget", "deadline"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Masalan: Korporativ sayt"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Loyiha haqida batafsil yozing...",
                    "rows": 5,
                }
            ),
            "category": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Web, Mobil, Dizayn..."}
            ),
            "budget": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Byudjet (so'm)", "step": "0.01"}
            ),
            "deadline": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }
        labels = {
            "title": "Loyiha nomi",
            "description": "Loyiha tavsifi",
            "category": "Kategoriya",
            "budget": "Byudjet",
            "deadline": "Muddat",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["deadline"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean_budget(self):
        budget = self.cleaned_data.get("budget")
        if budget is None:
            return budget
        if budget <= 0:
            raise forms.ValidationError("Byudjet 0 dan katta bo'lishi kerak.")
        return budget

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if not deadline:
            return deadline
        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
        if deadline <= timezone.now():
            raise forms.ValidationError("Muddat hozirgi vaqtdan keyin bo'lishi kerak.")
        return deadline


class BidCreateForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["price", "message"]
        widgets = {
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Taklif narxi", "step": "0.01"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Qisqacha taklif xabari...",
                    "rows": 3,
                }
            ),
        }
        labels = {"price": "Taklif narxi", "message": "Xabar"}

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None:
            return price
        if price <= 0:
            raise forms.ValidationError("Taklif narxi 0 dan katta bo'lishi kerak.")
        return price

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) < 5:
            raise forms.ValidationError("Xabar kamida 5 ta belgidan iborat bo'lishi kerak.")
        return message


class FreelancerSettingsForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "title",
            "location",
            "website",
            "telegram",
            "hourly_rate",
            "bio",
            "categories",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "telegram": forms.TextInput(attrs={"class": "form-control"}),
            "hourly_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "bio": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Qisqacha bio"}
            ),
        }
        labels = {
            "first_name": "Ism",
            "last_name": "Familiya",
            "email": "Email",
            "phone": "Telefon raqam",
            "title": "Kasb nomi",
            "location": "Manzil",
            "website": "Veb-sayt",
            "telegram": "Telegram",
            "hourly_rate": "Soatlik narx",
            "bio": "Bio",
            "categories": "Kategoriyalar",
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return ""
        normalized = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        if not normalized or normalized in {"+", ""}:
            raise forms.ValidationError("Telefon raqami noto'g'ri kiritildi")
        qs = CustomUser.objects.filter(phone=normalized).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Bu telefon raqami allaqachon mavjud")
        return normalized


class ClientSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone", "bio", "location", "website", "telegram"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "telegram": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Qisqacha bio"}
            ),
        }
        labels = {
            "first_name": "Ism",
            "last_name": "Familiya",
            "email": "Email",
            "phone": "Telefon raqam",
            "location": "Manzil",
            "website": "Veb-sayt",
            "telegram": "Telegram",
            "bio": "Bio",
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return ""
        normalized = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        if not normalized or normalized in {"+", ""}:
            raise forms.ValidationError("Telefon raqami noto'g'ri kiritildi")
        qs = CustomUser.objects.filter(phone=normalized).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Bu telefon raqami allaqachon mavjud")
        return normalized


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(
                attrs={"class": "form-control"},
                choices=[(i, f"{i} / 5") for i in range(1, 6)],
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Qisqacha fikr (ixtiyoriy)",
                }
            ),
        }
        labels = {"rating": "Baho", "comment": "Izoh"}
