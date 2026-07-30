import requests
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import AddAnimeSerializer, UserSerializer
from .models import Anime, UserAnime

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class AddAnimeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddAnimeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        mal_id = serializer.validated_data["mal_id"]
        watch_status = serializer.validated_data["status"]

        anime = Anime.objects.filter(mal_id=mal_id).first()

        # Fetch from Jikan API if anime doesn't exist
        if anime is None:
            response = requests.get(
                f"fhttps://api.jikan.moe/v4/anime/{mal_id}"
            )

            if response.status_code != 200:
                return Response(
                    {"error": "Anime not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            anime_data = response.json()["data"]
            anime = Anime.objects.create(
                mal_id = anime_data["mal_id"],
                title = anime_data["title"],
                image_url = anime_data["images"]["jpg"]["image_url"],
                episodes = anime_data["episodes"] or 0,
            )

            # Prevent duplicate entries
            if UserAnime.objects.filter(
                user = request.user,
                anime = anime
            ).exists():
                return Response(
                    {"error": "Anime already in your list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            user_anime = UserAnime.object.create(
                user=request.user,
                anime=anime,
                status=watch_status,
            )

        return Response(
            {"message": "Anime added successfully"},
            status=status.HTTP_201_CREATED,
        )