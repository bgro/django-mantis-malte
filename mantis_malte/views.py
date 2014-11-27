__author__ = 'Philipp Lang'

from braces.views import LoginRequiredMixin

from django.forms.formsets import formset_factory
from django.views.generic.list import ListView

from dingos.models import FactTerm

from . import MANTIS_MALTE_TEMPLATE_FAMILY
from .forms import FactTermCorrelationEditForm
from .models import FactTermWeight

class FactTermWeightEdit(ListView,LoginRequiredMixin):
    model = FactTerm

    template_name = 'mantis_malte/%s/FactTermWeightEdit.html' % MANTIS_MALTE_TEMPLATE_FAMILY

    form_class = formset_factory(FactTermCorrelationEditForm, extra=0)
    formset = None

    def get_context_data(self, **kwargs):
        context = super(FactTermWeightEdit, self).get_context_data(**kwargs)
        context['formset'] = self.formset
        return context

    def get(self, request, *args, **kwargs):
        print("Entering GET METHOD")
        initial = []

        qs = FactTerm.objects.all().values('term','factterm_set__weight')
        for row in qs:
            initial.append({
                'fact_term' : row['term'],
                'weight' : row['factterm_set__weight']
            })

        self.formset = self.form_class(initial=initial)
        return super(FactTermWeightEdit, self).get(request, *args, **kwargs)
