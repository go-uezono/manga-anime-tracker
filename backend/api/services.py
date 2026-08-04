from fractions import Fraction
import requests, time, re
from rest_framework.exceptions import APIException, NotFound
from .models import Anime, Franchise

ANILIST_URL = "https://graphql.anilist.co"

ANIME_BY_ID_QUERY = """
query ($id: Int) {
    Media(id: $id, type: ANIME) {
        id
        title { romaji }
        coverImage { large }
        episodes
    }
}
"""

SEARCH_QUERY = """
query ($search: String) {
    Page(perPage: 10) {
        media(search: $search, type: ANIME) {
            id
            title { romaji }
            coverImage { large }
            episodes
        }
    }
}
"""

def fetch_from_anilist(query, variables, retries=2, timeout=5):
    last_exception = None

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                ANILIST_URL, 
                json={"query": query, "variables": variables}, 
                timeout=timeout,
            )

            if response.status_code == 504 and attempt < retries:
                time.sleep(1)
                continue

            return response
        
        except requests.RequestException as e:
            last_exception = e 
            if attempt < retries:
                time.sleep(1)
                continue

    raise APIException("Unable to contact Anilist.") from last_exception

# Helper method to get/create anime from Anilist api
def get_or_create_anime(anilist_id):
    anime = Anime.objects.filter(anilist_id=anilist_id).first()

    if anime:
        return anime
    
    response = fetch_from_anilist(ANIME_BY_ID_QUERY, {"id": anilist_id})
    response.raise_for_status()
    payload = response.json()

    if payload.get("errors") or not payload["data"]["Media"]:
        raise NotFound("Anime not found.")
    
    data = payload["data"]["Media"]
    title = data["title"]["romaji"]
    franchise = get_or_create_franchise(title)

    anime = Anime.objects.create(
        anilist_id=data["id"],
        title=data["title"]["romaji"],
        image_url=data["coverImage"]["large"],
        episodes=data["episodes"] or 0,
        franchise=franchise,
    )

    return anime

SEASON_PATTERNS = [
    r"\bseason\s*\d+\b",
    r"\b\d+(st|nd|rd|th)\s*season\b",
    r"\bpart\s*\d+\b",
    r"\bfinal season\b",
    r"\b(i{1,3}|iv|v|vi{1,3})\b",
    r":\s*,*$",
    r"\s+\d+$",
]

def strip_name(title):
    t = title.lower()

    m = re.search(r"season\s*(\d+)", t)
    if m:
        return int(m.group(1))
    
    m = re.search(r"(\d+)(st|nd|rd|th)\s*season", t)
    if m:
        return int(m.group(1))
    
    m = re.search(r"part\s*(\d+)", t)
    if m:
        return int(m.group(1))
    
    roman_map = {
        "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8
    }
    m = re.search(r"\b(ii|iii|iv|v|vi|vii|viii)\b", t)
    if m:
        return roman_map[m.group(1)]
    
    m = re.search(r"\s(\d+)$", t)
    if m: 
        return int(m.group(1))
    
    return 1

def normalize_title(title):
    t = title.lower()

    for pattern in SEASON_PATTERNS:
        t = re.sub(pattern, "", t)
    
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return t   

def get_or_create_franchise(title):
    normalized = normalize_title(title)
    franchise, created = Franchise.objects.get_or_create(
        normalized_name=normalized,
        defaults={"name": title},
    )

    if not created:
        curr_season = strip_name(franchise.name)
        next_season = strip_name(title)

        if next_season < curr_season:
            franchise.name = title
            franchise.save()

    return franchise