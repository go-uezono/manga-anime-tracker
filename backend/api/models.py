from django.db import models
from django.contrib.auth.models import User

# Anime model
class Anime(models.Model):
    mal_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    image_url = models.URLField()
    episodes = models.PositiveIntegerField()

    def __str__(self):
        return self.title

# UserAnime model
class UserAnime(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Plan to watch"
        WATCHING = "watching", "Watching"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="anime_list")
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name="user_entries")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )

    progress = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "anime"],
                name="unique_user_anime",
            )
        ]
