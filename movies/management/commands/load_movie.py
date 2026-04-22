import requests
from datetime import date
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, Genre, Person, Job, MovieCredit

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE = "https://image.tmdb.org/t/p/w500"

def tmdb_get(endpoint, params={}):
    params["api_key"] = settings.TMDB_API_KEY
    params["language"] = "es-MX"
    r = requests.get(f"{TMDB_BASE}{endpoint}", params=params)
    return r.json() if r.status_code == 200 else None

class Command(BaseCommand):
    help = "Carga películas desde TMDB"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=3)
        parser.add_argument("--tipo", type=str, default="popular",
            choices=["popular", "top_rated", "now_playing", "upcoming"])

    def handle(self, *args, **options):
        pages = options["pages"]
        tipo  = options["tipo"]
        self.stdout.write(f"\n🎬 Cargando '{tipo}' — {pages} páginas...\n")

        for g in (tmdb_get("/genre/movie/list") or {}).get("genres", []):
            Genre.objects.get_or_create(id=g["id"], defaults={"name": g["name"]})

        guardadas = 0
        for page in range(1, pages + 1):
            self.stdout.write(f"  Página {page}/{pages}...")
            for item in (tmdb_get(f"/movie/{tipo}", {"page": page}) or {}).get("results", []):
                if self.guardar(item["id"]):
                    guardadas += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ {guardadas} películas guardadas.\n"))

    def guardar(self, tmdb_id):
        if Movie.objects.filter(tmdb_id=tmdb_id).exists():
            return False
        m = tmdb_get(f"/movie/{tmdb_id}")
        if not m or not m.get("release_date") or not m.get("title"):
            return False

        movie = Movie.objects.create(
            title       = m["title"][:80],
            overview    = m.get("overview", ""),
            release_date= date.fromisoformat(m["release_date"]),
            running_time= m.get("runtime") or 0,
            budget      = m.get("budget") or None,
            revenue     = m.get("revenue") or None,
            tmdb_id     = tmdb_id,
            poster_path = f"{TMDB_IMAGE}{m['poster_path']}" if m.get("poster_path") else None,
        )

        for g in m.get("genres", []):
            genre, _ = Genre.objects.get_or_create(id=g["id"], defaults={"name": g["name"]})
            movie.genres.add(genre)

        creditos = tmdb_get(f"/movie/{tmdb_id}/credits")
        if creditos:
            job_actor, _ = Job.objects.get_or_create(name="Acting")
            job_dir,   _ = Job.objects.get_or_create(name="Director")
            for c in creditos.get("crew", []):
                if c.get("job") == "Director":
                    p, _ = Person.objects.get_or_create(name=c["name"][:128])
                    MovieCredit.objects.get_or_create(person=p, movie=movie, job=job_dir)
                    break
            for a in creditos.get("cast", [])[:5]:
                p, _ = Person.objects.get_or_create(name=a["name"][:128])
                MovieCredit.objects.get_or_create(person=p, movie=movie, job=job_actor)

        self.stdout.write(f"    ✓ {movie.title}")
        return True



