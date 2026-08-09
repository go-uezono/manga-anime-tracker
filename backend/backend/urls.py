from django.contrib import admin
from django.urls import path, include
from api.views import AddAnimeView, CreateUserView, ListUserAnimeView, RecentAnimeView, SearchAnimeView, UserAnimeDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/user/register/", CreateUserView.as_view(), name="register"),
    path("api/token/", TokenObtainPairView.as_view(), name="get_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api-auth/", include("rest_framework.urls")),
    path("api/anime/search/", SearchAnimeView.as_view(), name="search-anime"),
    path("api/anime/add/", AddAnimeView.as_view(), name="add-anime"),
    path("api/anime/list/", ListUserAnimeView.as_view(), name="list-anime"),
    path("api/anime/<int:pk>/", UserAnimeDetailView.as_view(), name="anime-detail"),
    path("api/anime/recent/", RecentAnimeView.as_view(), name="recent-anime"),
]
