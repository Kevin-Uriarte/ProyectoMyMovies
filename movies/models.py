from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=80)
    
    def __str__(self):
        return self.name
    
class Person(models.Model):
    name = models.CharField(max_length=128)
    
    def __str__(self):
        return self.name


class Job(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Movie(models.Model):
    # Movie guarda la parte persistente del proyecto: reseñas, likes y referencias locales a TMDB.
    title = models.CharField(max_length=80)
    overview = models.TextField()
    release_date = models.DateField()
    running_time = models.IntegerField()
    budget = models.IntegerField(blank=True, null=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    revenue = models.IntegerField(blank=True, null=True)
    poster_path = models.URLField(blank=True, null=True)
    genres = models.ManyToManyField(Genre)
    credits = models.ManyToManyField(Person, through='MovieCredit')

    def __str__(self):
        return f'{self.title} {self.release_date}'


class MovieCredit(models.Model):
    # Modelo intermedio para relacionar una película con una persona y su rol.
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)


class MovieLike(models.Model):
    # Aquí se guarda la interacción simple del usuario con una película.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    review = models.TextField(blank=True)

class MovieReview(models.Model):
    # MovieReview representa la reseña formal con calificación y comentario.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    review = models.TextField(blank=True)
    title = models.TextField(blank=False, null=False, default="Reseña")
