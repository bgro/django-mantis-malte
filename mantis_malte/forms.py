
# Copyright (c) Siemens AG, 2015
#
# This file is part of MANTIS.  MANTIS is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or(at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#



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