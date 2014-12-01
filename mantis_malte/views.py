__author__ = 'Philipp Lang'

from braces.views import LoginRequiredMixin

from django.forms.formsets import formset_factory
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from dingos.models import FactTerm, InfoObject, InfoObject2Fact, Fact

from . import MANTIS_MALTE_TEMPLATE_FAMILY
from .forms import FactTermCorrelationEditForm
from .models import FactTermWeight

class FactTermWeightEdit(ListView,LoginRequiredMixin):
    model = FactTerm

    template_name = 'mantis_malte/%s/edits/FactTermWeightEdit.html' % MANTIS_MALTE_TEMPLATE_FAMILY

    form_class = formset_factory(FactTermCorrelationEditForm, extra=0)
    formset = None

    @property
    def queryset(self):
        queryset = FactTerm.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(FactTermWeightEdit, self).get_context_data(**kwargs)
        context['formset'] = self.formset
        context['title'] = 'Content Title Test'
        return context

    def get(self, request, *args, **kwargs):
        #TODO paginate factterms
        print("Entering GET METHOD")
        initial = []


        for row in self.queryset.order_by('term').values('term','factterm_set__weight'):
            if row['term'] != '':
                initial.append({
                    'fact_term' : row['term'],
                    'weight' : row['factterm_set__weight']
                })

        self.formset = self.form_class(initial=initial)
        return super(FactTermWeightEdit, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("Entering POST METHOD")
        #TODO there shouldn't be double values in database
        self.formset = self.form_class(request.POST.dict())
        if self.formset.is_valid() and request.user.is_authenticated():
            queryset = self.queryset
            for form in self.formset:
                factterm = queryset.filter(term=form.cleaned_data["fact_term"])[0]
                if form.cleaned_data["weight"] in ['', None]:
                    try:
                        facttermweight = FactTermWeight.objects.get(fact_term=factterm)
                        facttermweight.delete()
                    except FactTermWeight.DoesNotExist:
                        continue


                else:
                    try:
                        facttermweight = FactTermWeight.objects.get(fact_term=factterm)
                        if form.cleaned_data["weight"] != facttermweight.weight:
                            facttermweight.weight = form.cleaned_data["weight"]
                            facttermweight.save()
                    except FactTermWeight.DoesNotExist:
                        facttermweight_new = FactTermWeight(fact_term=factterm,
                                                            weight=form.cleaned_data["weight"])
                        facttermweight_new.save()
        return self.get(request, *args, **kwargs)

class InfoObjectCorrelationView(DetailView, LoginRequiredMixin):
    #TODO list view with correlation
    model = InfoObject
    threshold = 0.4

    def get_context_data(self, **kwargs):
        context = super(InfoObjectCorrelationView, self).get_context_data(**kwargs)
        return context

    def get_facts(self):
        #TODO get all associated facts which weight is bigger than defined threshold in self.threshold
        pk = self.kwargs['pk']
        facts = []

        def get_facts_rec():
            facts = FactTerm.objects.filter(fact__iobject_thru__iobject=pk).values_list(*['fact__id','fact__value_iobject_id'])
            #TODO value_iobject_id != none --> go on with collecting facts...
            #TODO value_iobject_id == none --> fact_value prüfen...
            #factterm_set__weight__gte=self.threshold,
            print "#############"
            print facts.query
            print facts

        get_facts_rec()


    def get(self, request, *args, **kwargs):
        self.get_facts()
        #TODO template context
        #TODO create template (InfoObjects which could correlate; Package containing them; correlating facts)


#TODO Bernd: Multiple Values in DB; Algo resursive search and then join?




