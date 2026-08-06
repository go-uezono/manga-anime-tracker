from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import generics, status
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
from .services import SEARCH_QUERY, fetch_from_anilist, get_or_create_anime, strip_name

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

        response = fetch_from_anilist(SEARCH_QUERY, {"search": query})
        response.raise_for_status()
        payload = response.json()

        results = [
            {
                "anilist_id": item["id"],
                "title": item["title"]["romaji"],
                "image_url": item["coverImage"]["large"],
                "episodes": item.get("episodes") or 0,
            }
            for item in payload["data"]["Page"]["media"]
        ]

        return Response(results)

class AddAnimeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddAnimeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated = serializer.validated_data
        anime = get_or_create_anime(validated["anilist_id"])
        progress = anime.episodes if validated["status"] == "completed" else 0

        try:
            user_anime = UserAnime.objects.create(
                user=request.user, 
                anime=anime, 
                status=validated["status"],
                progress=progress,
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

class ListUserAnimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = UserAnime.objects.filter(
            user=request.user
        ).select_related("anime", "anime__franchise")

        grouped = {}

        for entry in entries:
            key = entry.anime.franchise.name if entry.anime.franchise else entry.anime.title
            grouped.setdefault(key, []).append(entry)
        
        response = {}
        for key, group_entries in grouped.items():
            sorted_entries = sorted(
                group_entries,
                key=lambda e: strip_name(e.anime.title)
            )
            response[key] = [UserAnimeSerializer(e).data for e in sorted_entries]

        return Response(response)

# Updates and deletes anime
class UserAnimeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatedUserAnimeSerializer

    def get_queryset(self):
        return UserAnime.objects.filter(
            user=self.request.user
        )
        