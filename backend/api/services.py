import requests, time
from rest_framework.exceptions import APIException, NotFound
from urllib3 import response
from .models import Anime

JIKAN_URL = "https://api.jikan.moe/v4/anime"

def fetch_from_jikan(url, params=None, retries=2, timeout=5):
    last_exception = None

    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)

            if response.status_code == 504:
                if attempt < retries:
                    time.sleep(1)
                    continue
                raise APIException("Jikan currently unavail")

            return response
        
        except requests.RequestException as e:
            last_exception = e 
            if attempt < retries:
                time.sleep(1)
                continue

    raise APIException("Unable to contact Jikan.") from last_exception

# Helper method to get/create anime from Jikan api
def get_or_create_anime(mal_id):
    anime = Anime.objects.filter(mal_id=mal_id).first()

    if anime:
        return anime
    
    response = fetch_from_jikan(f"{JIKAN_URL}/{mal_id}")
    
    data = response.json()["data"]
    anime = Anime.objects.create(
        mal_id=data["mal_id"],
        title=data["title"],
        image_url=data["images"]["jpg"]["image_url"],
        episodes=data["episodes"] or 0,
    )
    return anime