from django import forms
from movies.models import MovieReview

_input_cls = ("block w-full rounded-2xl border border-slate-200 bg-white/95 px-4 py-3 text-base "
              "text-slate-900 shadow-sm placeholder:text-slate-400 "
              "focus:border-sky-400 focus:outline-none focus:ring-4 focus:ring-sky-300/25 sm:text-sm/6")

_num_cls   = ("block w-full rounded-2xl border border-slate-200 bg-white/95 px-4 py-3 text-base "
              "text-slate-900 shadow-sm focus:border-sky-400 focus:outline-none "
              "focus:ring-4 focus:ring-sky-300/25 sm:text-sm/6")


class MovieCommentForm(forms.Form):
    review = forms.CharField(
        label="Comentario", min_length=5, required=True,
        widget=forms.Textarea(attrs={"class": _input_cls, "rows": 3}))


class MovieReviewForm(forms.ModelForm):
    class Meta:
        model = MovieReview
        fields = ['title', 'rating', 'review']
        labels = {'title': 'Título', 'rating': 'Calificación (1-100)', 'review': 'Reseña'}
        widgets = {
            'title':  forms.TextInput(attrs={"class": _input_cls,
                                             "placeholder": "Título de tu reseña"}),
            'rating': forms.NumberInput(attrs={"class": _num_cls,
                                               "min": 1, "max": 100}),
            'review': forms.Textarea(attrs={"class": _input_cls, "rows": 4,
                                            "placeholder": "Escribe tu reseña…"}),
        }
