from django import forms
from django.db import models
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)