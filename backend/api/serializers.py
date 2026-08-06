from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Anime, UserAnime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class AnimeSerializer(serializers.ModelSerializer):
    franchise = serializers.CharField(
        source="franchise.name",
        read_only=True,
        default=None,
    )

    class Meta:
        model = Anime
        fields = [
            "anilist_id",
            "title",
            "image_url",
            "episodes",
            "franchise",
        ]

class UserAnimeSerializer(serializers.ModelSerializer):
    anime = AnimeSerializer(read_only=True)

    class Meta: 
        model = UserAnime
        fields = [
            "id",
            "anime",
            "status",
            "progress"
        ]

class AddAnimeSerializer(serializers.Serializer):
    anilist_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=UserAnime.Status.choices)

class UpdatedUserAnimeSerializer(serializers.ModelSerializer):
    def validate(self, data):
        instance = self.instance
        anime = instance.anime if instance else None
        status_value = data.get("status", instance.status if instance else None)
        progress = data.get("progress")

        # Autofill episodes to x/x if marked as completed
        if status_value == "completed" and anime and anime.episodes:
            if progress is None or progress < anime.episodes:
                data["progress"] = anime.episodes

        # Checks progress bounds (episode count)
        elif anime and progress is not None and anime.episodes and progress > anime.episodes:
            raise serializers.ValidationError(
                {"progress": "Progress can't exceed total episode count."}
            )
        return data

    class Meta:
        model = UserAnime
        fields = ["status", "progress"]

