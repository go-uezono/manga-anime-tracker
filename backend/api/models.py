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
    
    STATUS_OPTIONS = [
        ("planned", "Plan to watch"), 
        ("watching", "Watching"),
        ("completed", "Completed")
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    anime = models.ForeignKey(
        Anime,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_OPTIONS,
        default="planned"
    )

    progress = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "anime")
