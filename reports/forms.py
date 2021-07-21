from django import forms
from django.db import models
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model =  Report
        fields = ('name', 'remarks')