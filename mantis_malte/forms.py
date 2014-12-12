__author__ = 'Philipp Lang'

from django import forms
from .models import AssignmentName, FactTerm2Weight, FactTerm

class FactTermCorrelationEditForm(forms.Form):
    """
    Form for editing the Weight of the FactTerms
    """
    weight = forms.FloatField(required=False, min_value=0.0, max_value=1.0, widget=forms.TextInput(attrs={'placeholder': 'Enter new Weight'}))
    #TODO minimize multiple querys per ChoiceField
    #http://stackoverflow.com/questions/8176200/caching-queryset-choices-for-modelchoicefield-or-modelmultiplechoicefield-in-a-d
    #choice prefetch
    assignment_name = forms.ModelChoiceField(required=False, queryset=AssignmentName.objects, cache_choices=True)
    factterm = forms.ModelChoiceField(queryset=FactTerm.objects,widget=forms.HiddenInput())

class CorrelationViewForm(forms.Form):
    """
    Form to choose Assignment Name
    """
    assignment_name = forms.ModelChoiceField(required=True, queryset=AssignmentName.objects, cache_choices=True)