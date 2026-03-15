from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from base.models import TimeStamped
from users.models import CustomUser

# Create your models here.
class Project(TimeStamped):

    class StatusChoices(models.TextChoices):
        OPEN = "Open", "open"
        IN_PROGRESS = "In progress", "in_progress"
        COMPLETED = "Completed", "completed"
        CANCELLED = "Cancelled", "cancelled"

    title = models.CharField(max_length=256)
    description = models.TextField()
    category = models.CharField(max_length=120, blank=True)
    budget = models.DecimalField(max_digits=13, decimal_places=2)
    deadline = models.DateTimeField()
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="projects")
    progress = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=12, choices=StatusChoices.choices, default=StatusChoices.OPEN)

    def __str__(self):
        return self.title


class Bid(TimeStamped):

    class StatusChoices(models.TextChoices):
        PENDING = "Pending", "pending"
        ACCEPTED = "Accepted", "accepted"
        REJECTED = "Rejected", "rejected"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, )
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=13, decimal_places=2)
    message = models.CharField(max_length=256)
    status = models.CharField(max_length=9, choices=StatusChoices.choices)

    def __str__(self):
        return f"{self.freelancer.username} - {self.project.title}"
    


class Contract(TimeStamped):

    class StatusChoices(models.TextChoices):
        ACTIVE = "Active", "active"
        FINISHED = "Finished", "finished"
        CANCELLED = "Cancelled", "cancelled"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="client_contracts")
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="freelancer_contracts")
    agreed_price = models.DecimalField(max_digits=13, decimal_places=2)
    status = models.CharField(max_length=10, choices=StatusChoices.choices)

    def __str__(self):
        return f"{self.freelancer.username} - {self.client.username} - {self.project.title}"


class Review(TimeStamped):
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name="review")
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews_given")
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.client.username} -> {self.freelancer.username} ({self.rating})"

    @property
    def author(self):
        return self.client
