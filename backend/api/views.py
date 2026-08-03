from django.contrib.auth.models import User
from django.db import IntegrityError
import requests
from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserAnime
from .serializers import (
    AddAnimeSerializer,
    UpdatedUserAnimeSerializer,
    UserAnimeSerializer,
    UserSerializer,
)
from .services import JIKAN_URL, fetch_from_jikan, get_or_create_anime

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class SearchAnimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"error": "Query param 'q' is required."}, 
                status=400
            )

        response = fetch_from_jikan(JIKAN_URL, params={"q": query, "limit": 10})
        response.raise_for_status()

        results = [
            {
                "mal_id": item["mal_id"],
                "title": item["title"],
                "image_url": item["images"]["jpg"]["image_url"],
                "episodes": item.get("episodes") or 0,
            }
            for item in response.json().get("data", [])
        ]

        return Response(results)


class AddAnimeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddAnimeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        anime = get_or_create_anime(validated["mal_id"])

        try:
            user_anime = UserAnime.objects.create(
                user=request.user, anime=anime, status=validated["status"]
            )
        except IntegrityError:
            return Response(
                {"error": "Anime already in your list."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "message": "Anime added successfully",
                "anime": UserAnimeSerializer(user_anime).data,
            },
            status=status.HTTP_201_CREATED,
        )

class ListUserAnimeView(generics.ListAPIView):
    serializer_class = UserAnimeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAnime.objects.filter(
            user=self.request.user
        ).select_related("anime")

# Updates and deletes anime
class UserAnimeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatedUserAnimeSerializer

    def get_queryset(self):
        return UserAnime.objects.filter(
            user=self.request.user
        )
        