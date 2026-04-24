from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from movies.models import Movie, MovieReview, Person, MovieLike
from movies.forms import MovieReviewForm, MovieCommentForm
from movies import tmdb_client as tmdb


# ─── helpers ────────────────────────────────────────────────────────────────

def _movie_or_tmdb(movie_id):
    """
    Return (movie_db, tmdb_data).
    movie_db  → Movie ORM object if it exists locally, else None
    tmdb_data → dict from TMDB API (always fetched for live info)
    """
    movie_db = Movie.objects.filter(tmdb_id=movie_id).first()
    tmdb_data = tmdb.get_movie_detail(movie_id)
    return movie_db, tmdb_data


def _get_safe_next_url(request, fallback_url):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return fallback_url


# ─── index / home ────────────────────────────────────────────────────────────

def index(request):
    """
    Página principal: películas en cartelera desde TMDB.
    Tiene paginación simple (botón Siguiente / Anterior).
    """
    page = int(request.GET.get('page', 1))
    movies = tmdb.get_now_playing(page=page)
    return render(request, 'movies/index.html', {
        'movies': movies,
        'page': page,
    })


# ─── more movies (HTMX partial) ──────────────────────────────────────────────

def more_movies(request):
    """HTMX endpoint: devuelve solo las tarjetas de películas (sin layout)."""
    page = int(request.GET.get('page', 2))
    movies = tmdb.get_now_playing(page=page)
    return render(request, 'movies/partials/movie_cards.html', {
        'movies': movies,
        'page': page,
    })


# ─── all movies (local DB) ───────────────────────────────────────────────────

def all_movies(request):
    movies = Movie.objects.all().order_by('-release_date')
    return render(request, 'movies/allmovies.html', {'objetos': movies})


# ─── recomendadas ────────────────────────────────────────────────────────────

def recommended(request):
    """Página de películas recomendadas (populares de TMDB)."""
    movies = tmdb.get_popular(page=1)
    return render(request, 'movies/recommended.html', {'movies': movies})


# ─── detalle de película ─────────────────────────────────────────────────────

def movie(request, movie_id):
    """
    Detalle de una película usando tmdb_id.
    Primero busca en DB local; si no existe muestra datos de TMDB directamente.
    """
    movie_db = Movie.objects.filter(tmdb_id=movie_id).first()
    tmdb_data = tmdb.get_movie_detail(movie_id)
    credits = tmdb.get_movie_credits(movie_id)
    cast = credits.get('cast', [])[:10]
    crew = [c for c in credits.get('crew', []) if c.get('job') == 'Director'][:1]
    recs = tmdb.get_recommendations(movie_id)[:6]

    reviews = MovieReview.objects.filter(
        movie=movie_db).order_by('-id') if movie_db else MovieReview.objects.none()

    review_form = MovieReviewForm()
    user_review = None
    if request.user.is_authenticated and movie_db:
        user_review = MovieReview.objects.filter(
            movie=movie_db, user=request.user).first()

    return render(request, 'movies/movie.html', {
        'movie': movie_db,
        'tmdb': tmdb_data,
        'cast': cast,
        'crew': crew,
        'recommendations': recs,
        'reviews': reviews,
        'review_form': review_form,
        'user_review': user_review,
        'movie_id': movie_id,
    })


# ─── detalle de actor ────────────────────────────────────────────────────────

def actor_detail(request, person_id):
    """Detalle de un actor/director usando person_id de TMDB."""
    person_db = Person.objects.filter(pk=person_id).first()
    actor = tmdb.get_person_detail(person_id)
    credits = tmdb.get_person_credits(person_id)
    actor_movies = credits.get('cast', [])[:12]
    return render(request, 'movies/actor_detail.html', {
        'actor': actor,
        'person_db': person_db,
        'movies': actor_movies,
    })


# ─── reseñas de una película ─────────────────────────────────────────────────

def movie_reviews(request, movie_id):
    movie_db = get_object_or_404(Movie, tmdb_id=movie_id)
    return render(request, 'movies/reviews.html', {'movie': movie_db})


# ─── agregar reseña ──────────────────────────────────────────────────────────

@login_required
def add_review(request, movie_id):
    """
    Crea o actualiza la reseña del usuario para una película.
    Si la película no existe en DB local la crea primero.
    """
    # Asegurar que la película exista en DB
    movie_db = Movie.objects.filter(tmdb_id=movie_id).first()
    if not movie_db:
        tmdb_data = tmdb.get_movie_detail(movie_id)
        if not tmdb_data or not tmdb_data.get('title'):
            messages.error(request, 'Película no encontrada.')
            return redirect('index')
        from datetime import date
        movie_db = Movie.objects.create(
            title=tmdb_data['title'][:80],
            overview=tmdb_data.get('overview', ''),
            release_date=date.fromisoformat(tmdb_data['release_date']),
            running_time=tmdb_data.get('runtime') or 0,
            budget=tmdb_data.get('budget') or None,
            revenue=tmdb_data.get('revenue') or None,
            tmdb_id=movie_id,
            poster_path=(
                f"https://image.tmdb.org/t/p/w500{tmdb_data['poster_path']}"
                if tmdb_data.get('poster_path') else None
            ),
        )

    existing = MovieReview.objects.filter(
        user=request.user, movie=movie_db).first()

    if request.method == 'POST':
        form = MovieReviewForm(request.POST, instance=existing if existing else None)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie_db
            review.save()
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    status=204,
                    headers={'HX-Redirect': reverse('movie_detail', kwargs={'movie_id': movie_id})})
            messages.success(request, '¡Reseña guardada!')
            return redirect('movie_detail', movie_id=movie_id)
    else:
        form = MovieReviewForm(instance=existing)

    tmdb_data = tmdb.get_movie_detail(movie_id)
    template_name = 'movies/partials/movie_review_modal.html' if request.headers.get('HX-Request') else 'movies/movie_review_form.html'
    return render(request, template_name, {
        'movie_review_form': form,
        'movie': movie_db,
        'tmdb': tmdb_data,
        'movie_id': movie_id,
    })


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(
        MovieReview.objects.select_related('movie'),
        id=review_id,
        user=request.user,
    )
    fallback_url = reverse('movie_detail', kwargs={'movie_id': review.movie.tmdb_id})
    next_url = _get_safe_next_url(request, fallback_url)
    review.delete()

    if request.headers.get('HX-Request'):
        return HttpResponse(status=204, headers={'HX-Redirect': next_url})

    messages.success(request, 'Reseña eliminada.')
    return redirect(next_url)


# ─── agregar like/comentario ─────────────────────────────────────────────────

@login_required
def add_like(request, movie_id):
    movie_db = Movie.objects.filter(tmdb_id=movie_id).first()
    if not movie_db:
        return redirect('movie_detail', movie_id=movie_id)

    if request.method == 'POST':
        form = MovieCommentForm(request.POST)
        if form.is_valid():
            MovieLike.objects.update_or_create(
                user=request.user, movie=movie_db,
                defaults={'review': form.cleaned_data['review']})
            return redirect('movie_detail', movie_id=movie_id)
    else:
        form = MovieCommentForm()

    return render(request, 'movies/movie_comment_form.html',
                  {'form': form, 'movie': movie_db})


# ─── reseñas del usuario ─────────────────────────────────────────────────────

@login_required
def user_reviews(request):
    """Todas las reseñas escritas por el usuario autenticado."""
    reviews = MovieReview.objects.filter(
        user=request.user).select_related('movie').order_by('-id')
    return render(request, 'movies/user_reviews.html', {'reviews': reviews})


# ─── búsqueda ─────────────────────────────────────────────────────────────────

def search(request):
    query = request.GET.get('search', '').strip()
    results = []
    if query:
        import requests as req
        from django.conf import settings
        r = req.get(
            f"{settings.TMDB_BASE_URL}/search/movie",
            headers={"accept": "application/json"},
            params={"query": query, "language": "es-MX",
                    "api_key": settings.TMDB_API_KEY},
            timeout=5)
        if r.status_code == 200:
            results = r.json().get('results', [])
    return render(request, 'movies/search_results.html', {
        'results': results, 'query': query})
