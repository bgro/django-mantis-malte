__author__ = 'Philipp Lang'

from django import forms
from .models import AssignmentName, FactTerm2Weight

class FactTermCorrelationEditForm(forms.Form):
    """
    Form for editing the Weight of the FactTerms
    """
    weight = forms.FloatField(required=False, min_value=0.0, max_value=1.0, widget=forms.TextInput(attrs={'placeholder': 'Enter new Weight'}))
    #TODO minimize multiple querys
    assignment_name = forms.ModelChoiceField(required=False, queryset=AssignmentName.objects)