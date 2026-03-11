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
    