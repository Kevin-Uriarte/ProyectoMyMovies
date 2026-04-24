"""
TMDB API client — fetches live data when a movie isn't in the local DB.
All views that need live TMDB data import from here.
"""
import requests
from django.conf import settings

def _headers():
    token = settings.TMDB_API_TOKEN
    if token:
        return {"Authorization": f"Bearer {token}", "accept": "application/json"}
    return {"accept": "application/json"}

def _params(extra={}):
    p = {"language": "es-MX"}
    if not settings.TMDB_API_TOKEN:
        p["api_key"] = settings.TMDB_API_KEY
    p.update(extra)
    return p

BASE = settings.TMDB_BASE_URL

def get_now_playing(page=1):
    r = requests.get(f"{BASE}/movie/now_playing",
                     headers=_headers(), params=_params({"page": page}), timeout=5)
    return r.json().get("results", []) if r.status_code == 200 else []

def get_popular(page=1):
    r = requests.get(f"{BASE}/movie/popular",
                     headers=_headers(), params=_params({"page": page}), timeout=5)
    return r.json().get("results", []) if r.status_code == 200 else []

def get_movie_detail(tmdb_id):
    r = requests.get(f"{BASE}/movie/{tmdb_id}",
                     headers=_headers(), params=_params(), timeout=5)
    return r.json() if r.status_code == 200 else {}

def get_movie_credits(tmdb_id):
    r = requests.get(f"{BASE}/movie/{tmdb_id}/credits",
                     headers=_headers(), params=_params(), timeout=5)
    return r.json() if r.status_code == 200 else {}

def get_recommendations(tmdb_id):
    r = requests.get(f"{BASE}/movie/{tmdb_id}/recommendations",
                     headers=_headers(), params=_params(), timeout=5)
    return r.json().get("results", []) if r.status_code == 200 else []

def get_person_detail(person_id):
    r = requests.get(f"{BASE}/person/{person_id}",
                     headers=_headers(), params=_params(), timeout=5)
    return r.json() if r.status_code == 200 else {}

def get_person_credits(person_id):
    r = requests.get(f"{BASE}/person/{person_id}/movie_credits",
                     headers=_headers(), params=_params(), timeout=5)
    return r.json() if r.status_code == 200 else {}

def get_user_reviews_tmdb(tmdb_id):
    r = requests.get(f"{BASE}/movie/{tmdb_id}/reviews",
                     headers=_headers(), params=_params(), timeout=5)
    return r.json().get("results", []) if r.status_code == 200 else []