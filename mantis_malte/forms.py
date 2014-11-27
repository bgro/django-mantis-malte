__author__ = 'Philipp Lang'

from django import forms

class FactTermCorrelationEditForm(forms.Form):
    """
    Form for editing the Weight of the FactTerms
    """
    fact_term = forms.TextInput(required=True, widget=forms.TextInput(attrs={'readonly': True}))
    weight = forms.FloatField(required=True, min_value=0.0, max_value=1.0, widget=forms.TextInput(attrs={'placeholder': 'Enter new Weight'}))