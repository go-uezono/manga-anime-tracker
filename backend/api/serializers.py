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
        anime = self.instance.anime if self.instance else None
        progress = data.get("progress")

        if anime and progress is not None and anime.episodes and progress > anime.episodes:
            raise serializers.ValidationError(
                {"progress": "Progress can't exceed total episode count."}
            )
        return data

    class Meta:
        model = UserAnime
        fields = ["status", "progress"]

