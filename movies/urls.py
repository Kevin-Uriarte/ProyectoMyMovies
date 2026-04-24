from django.urls import path
from .views import (
    index, all_movies, movie, movie_reviews,
    add_review, add_like, recommended, actor_detail,
    user_reviews, search, more_movies, delete_review,
)

urlpatterns = [
    path('', index, name='index'),

    # Peliculas
    path('', all_movies, name='all_movies'),
    path('more/', more_movies, name='more_movies'),
    path('<int:movie_id>/', movie, name='movie_detail'),
    path('<int:movie_id>/reviews/', movie_reviews, name='movie_reviews'),
    path('<int:movie_id>/review/', add_review, name='add_review'),
    path('reviews/<int:review_id>/delete/', delete_review, name='delete_review'),
    path('<int:movie_id>/like/', add_like, name='add_like'),
    
    # Recomendadas
    path('recommended/', recommended, name='recommended'),

    # Actores
    path('actors/<int:person_id>/', actor_detail, name='actor_detail'),

    # Usuario
    path('my-reviews/', user_reviews, name='user_reviews'),

    # Búsqueda
    path('search/', search, name='search'),
]
