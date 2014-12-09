__author__ = 'Philipp Lang'

import django_filters

from .models import AssignmentName

class CorrelationFilter(django_filters.FilterSet):

    assignment =  django_filters.ModelChoiceFilter(queryset= AssignmentName.objects,
                                                    required=None,
                                                    label="Assignment",
                                                    to_field_name='id')
    class Meta:
        order_by = ['assignment_name']
        model = AssignmentName
