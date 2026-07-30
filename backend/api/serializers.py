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
    class Meta:
        model = Anime
        fields = [
            "mal_id",
            "title",
            "image_url",
            "episodes"
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
    mal_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices = [
            "planned",
            "watching",
            "completed"
        ]
    )
