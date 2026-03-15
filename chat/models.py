from django.db import models
from base.models import TimeStamped
from users.models import CustomUser


class Conversation(TimeStamped):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="conversations_user1")
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="conversations_user2")

    class Meta:
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"

    @staticmethod
    def normalize_users(user_a, user_b):
        return (user_a, user_b) if user_a.id < user_b.id else (user_b, user_a)

    @classmethod
    def get_or_create_between(cls, user_a, user_b):
        user1, user2 = cls.normalize_users(user_a, user_b)
        conversation, _ = cls.objects.get_or_create(user1=user1, user2=user2)
        return conversation

    def get_other_user(self, user):
        return self.user2 if self.user1 == user else self.user1


class Message(TimeStamped):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
