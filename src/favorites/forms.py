from django import forms

from .models import Favorite


class FavoriteForm(forms.ModelForm):

    class Meta:
        model = Favorite
        exclude = []
