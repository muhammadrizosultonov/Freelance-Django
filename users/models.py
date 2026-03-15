from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import TimeStamped

# Create your models here.
class CustomUser(AbstractUser, TimeStamped):

    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        FREELANCER = 'freelancer', 'Freelancer'

    role = models.CharField(max_length=13, choices=Role.choices, default=Role.CLIENT)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="users/avatar/", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    title = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    telegram = models.CharField(max_length=64, blank=True)
    hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cover_photo = models.ImageField(upload_to="users/cover/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    categories = models.ManyToManyField("Category", blank=True, related_name="users")

    @property
    def profile(self):
        return self

    @property
    def received_reviews(self):
        from django.apps import apps
        Review = apps.get_model("service", "Review")
        return Review.objects.filter(freelancer=self)


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=80)
    level = models.PositiveSmallIntegerField(default=50)

    class Meta:
        ordering = ("-level", "name")

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Experience(TimeStamped):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="experiences")
    title = models.CharField(max_length=120)
    company = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("-start_date",)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class PortfolioItem(TimeStamped):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="portfolio_items")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to="portfolio/", blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
