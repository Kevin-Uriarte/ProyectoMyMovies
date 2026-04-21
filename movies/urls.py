from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),

    path('movies/', all_movies, name='all_movies'),

    path('movie/<int:movie_id>/', movie, name='movie_detail'),

    path('movie/<int:movie_id>/reviews/', movie_reviews, name='movie_reviews'),

    path('movie/<int:movie_id>/add-review/', add_review, name='add_review'),

    path('movie/<int:movie_id>/add-like/', add_like, name='add_like'),

    path('saludo/<int:veces>/', saludo),
]
