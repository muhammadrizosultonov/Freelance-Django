from datetime import timedelta
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.utils import timezone
from .models import CustomUser, Skill, Experience, PortfolioItem
import random


OTP_RESEND_SECONDS = 60
OTP_CODE_TTL = timedelta(minutes=5)
OTP_VERIFY_TTL = timedelta(minutes=10)
OTP_ATTEMPTS = 5


def _cleanup_otp_session(session, now=None):
    now = now or timezone.now()
    otp_data = session.get("otp_login", {})
    expires_at = otp_data.get("expires_at")
    if expires_at and now.timestamp() > expires_at:
        session.pop("otp_login", None)
        otp_data = {}

    verified_data = session.get("otp_verified", {})
    verified_expires = verified_data.get("expires_at")
    if verified_expires and now.timestamp() > verified_expires:
        session.pop("otp_verified", None)
        verified_data = {}

    return otp_data, verified_data


def _first_form_error(form):
    if not form:
        return None
    non_field = form.non_field_errors()
    if non_field:
        return non_field[0]
    for field in form.fields:
        errors = form.errors.get(field)
        if errors:
            return errors[0]
    return None


def otp_context(request, form=None):
    now = timezone.now()
    otp_data, verified_data = _cleanup_otp_session(request.session, now=now)
    resent_in = None
    last_sent = otp_data.get("last_sent_at")
    if last_sent:
        last_sent_dt = timezone.datetime.fromtimestamp(last_sent, tz=timezone.get_current_timezone())
        delta = (now - last_sent_dt).total_seconds()
        if delta < OTP_RESEND_SECONDS:
            resent_in = OTP_RESEND_SECONDS - int(delta)

    identifier = otp_data.get("identifier")
    if not identifier and form is not None:
        identifier = (form.data.get("identifier") or "").strip()

    return {
        "otp_sent": bool(otp_data),
        "otp_verified": bool(verified_data),
        "identifier": identifier or "",
        "verified_identifier": verified_data.get("identifier", ""),
        "error": _first_form_error(form),
        "resent_in": resent_in,
    }

class SignupForm(UserCreationForm):

    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    role = forms.ChoiceField(choices=CustomUser.Role.choices)

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email", "phone", "role", "password1", "password2")


    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon mavjud")
        return email

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return ""
        normalized = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        if not normalized or normalized in {"+", ""}:
            raise forms.ValidationError("Telefon raqami noto'g'ri kiritildi")
        if CustomUser.objects.filter(phone=normalized).exists():
            raise forms.ValidationError("Bu telefon raqami allaqachon mavjud")
        return normalized


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "level"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Django"}),
            "level": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 100}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ["title", "company", "start_date", "end_date", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Senior Developer"}),
            "company": forms.TextInput(attrs={"class": "form-control", "placeholder": "TechUZ"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ["title", "description", "url", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Portfolio nomi"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
        }


class OtpSendForm(forms.Form):
    identifier = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None
        self.channel = None
        self.normalized = None
        self.resent_in = None

    def clean_identifier(self):
        identifier = (self.cleaned_data.get("identifier") or "").strip()
        if not identifier:
            raise forms.ValidationError("Email yoki telefon raqam kiriting.")

        try:
            validate_email(identifier)
            channel = "email"
            normalized = identifier.lower()
            user = CustomUser.objects.filter(email__iexact=normalized).first()
        except ValidationError:
            normalized = "".join(ch for ch in identifier if ch.isdigit() or ch == "+")
            digits = "".join(ch for ch in normalized if ch.isdigit())
            if len(digits) < 7:
                raise forms.ValidationError("Email yoki telefon raqam noto'g'ri kiritildi.")
            channel = "phone"
            user = CustomUser.objects.filter(phone=normalized).first()

        if not user:
            raise forms.ValidationError("Foydalanuvchi topilmadi.")

        self.user = user
        self.channel = channel
        self.normalized = normalized
        return normalized

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned

        otp_data = self.request.session.get("otp_login", {})
        last_sent = otp_data.get("last_sent_at")
        if last_sent:
            last_sent_dt = timezone.datetime.fromtimestamp(last_sent, tz=timezone.get_current_timezone())
            delta = (timezone.now() - last_sent_dt).total_seconds()
            if delta < OTP_RESEND_SECONDS:
                self.resent_in = OTP_RESEND_SECONDS - int(delta)
                raise forms.ValidationError("Kod qayta yuborish uchun 60 soniya kuting.")
        return cleaned

    def save(self):
        now = timezone.now()
        code_value = f"{random.randint(0, 999999):06d}"
        expires_at = now + OTP_CODE_TTL
        session = self.request.session
        session.pop("otp_verified", None)
        session["otp_login"] = {
            "user_id": self.user.id,
            "identifier": self.normalized,
            "hash": make_password(code_value),
            "expires_at": expires_at.timestamp(),
            "attempts_left": OTP_ATTEMPTS,
            "last_sent_at": now.timestamp(),
            "channel": self.channel,
        }

        if self.channel == "email":
            try:
                sent = send_mail(
                    "Kirish uchun tasdiqlash kodi",
                    f"Sizning tasdiqlash kodingiz: {code_value}\nKod 5 daqiqaga amal qiladi.",
                    settings.DEFAULT_FROM_EMAIL,
                    [self.user.email],
                    fail_silently=False,
                )
                if sent == 0:
                    raise ValueError("Email yuborilmadi")
            except Exception:
                self.add_error(None, "Email yuborilmadi. Kod terminalda ko'rinadi.")
        print(f"[OTP] Login code for {self.normalized}: {code_value}")
        return not self.errors


class OtpVerifyForm(forms.Form):
    code = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None
        self.identifier = ""

    def clean_code(self):
        code = (self.cleaned_data.get("code") or "").strip()
        if not code:
            raise forms.ValidationError("Kod kiriting.")
        return code

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned

        session = self.request.session
        otp_data = session.get("otp_login")
        if not otp_data:
            raise forms.ValidationError("Kod yuborilmagan. Avval kod oling.")

        expires_at = otp_data.get("expires_at")
        if not expires_at or timezone.now().timestamp() > expires_at:
            session.pop("otp_login", None)
            raise forms.ValidationError("Kod muddati tugagan. Qayta yuboring.")

        attempts_left = otp_data.get("attempts_left", 0)
        if attempts_left <= 0:
            session.pop("otp_login", None)
            raise forms.ValidationError("Urinishlar tugadi. Qayta kod oling.")

        code = cleaned.get("code", "")
        if not check_password(code, otp_data.get("hash", "")):
            otp_data["attempts_left"] = attempts_left - 1
            session["otp_login"] = otp_data
            raise forms.ValidationError("Kod noto'g'ri.")

        user = CustomUser.objects.filter(id=otp_data.get("user_id")).first()
        if not user:
            session.pop("otp_login", None)
            raise forms.ValidationError("Foydalanuvchi topilmadi.")

        self.user = user
        self.identifier = otp_data.get("identifier", "")
        return cleaned

    def save(self):
        session = self.request.session
        session.pop("otp_login", None)
        session["otp_verified"] = {
            "user_id": self.user.id,
            "identifier": self.identifier,
            "expires_at": (timezone.now() + OTP_VERIFY_TTL).timestamp(),
        }


class OtpPasswordForm(forms.Form):
    password = forms.CharField()
    remember_me = forms.BooleanField(required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned

        session = self.request.session
        verified_data = session.get("otp_verified")
        if not verified_data:
            raise forms.ValidationError("Avval tasdiqlash kodini kiriting.")
        expires_at = verified_data.get("expires_at")
        if not expires_at or timezone.now().timestamp() > expires_at:
            session.pop("otp_verified", None)
            raise forms.ValidationError("Tasdiqlash muddati tugagan. Qayta kod oling.")

        password = (cleaned.get("password") or "").strip()
        if not password:
            raise forms.ValidationError("Parolni kiriting.")

        user = CustomUser.objects.filter(id=verified_data.get("user_id")).first()
        if not user:
            session.pop("otp_verified", None)
            raise forms.ValidationError("Foydalanuvchi topilmadi.")

        auth_user = authenticate(self.request, username=user.username, password=password)
        if not auth_user:
            raise forms.ValidationError("Parol noto'g'ri.")

        self.user = auth_user
        return cleaned

    def login_user(self):
        self.request.session.pop("otp_verified", None)
        login(self.request, self.user, backend="django.contrib.auth.backends.ModelBackend")
        if self.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(1209600)
        else:
            self.request.session.set_expiry(0)
