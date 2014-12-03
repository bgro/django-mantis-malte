__author__ = 'Philipp Lang'

from braces.views import LoginRequiredMixin

from django.forms.formsets import formset_factory
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from dingos.models import FactTerm, InfoObject, InfoObject2Fact, Fact, vIO2FValue

from . import MANTIS_MALTE_TEMPLATE_FAMILY
from .forms import FactTermCorrelationEditForm
from .models import FactTermWeight


from datetime import datetime
from dingos.graph_traversal import follow_references

class FactTermWeightEdit(LoginRequiredMixin, ListView):
    model = FactTerm

    template_name = 'mantis_malte/%s/edits/FactTermWeightEdit.html' % MANTIS_MALTE_TEMPLATE_FAMILY

    form_class = formset_factory(FactTermCorrelationEditForm, extra=0)
    formset = None

    #TODO set title
    title = 'Title Test'

    def get_context_data(self, **kwargs):
        context = super(FactTermWeightEdit, self).get_context_data(**kwargs)
        context['formset'] = self.formset
        return context

    def get(self, request, *args, **kwargs):
        #TODO paginate factterms
        initial = []

        columns = ['term','attribute','factterm_set__weight']
        print(len(self.get_queryset().values(*columns).order_by('term')))
        print(self.get_queryset().values(*columns).order_by('term').query)
        for fact_term in self.get_queryset().values(*columns).order_by('term'):
                initial.append({
                    'fact_term' : "%s@%s" % (fact_term['term'], fact_term['attribute']) if fact_term['attribute'] else "%s" % (fact_term['term']),
                    'weight' : fact_term['factterm_set__weight']
                })
        self.formset = self.form_class(initial=initial)
        return super(FactTermWeightEdit, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("Entering POST METHOD")
        self.formset = self.form_class(request.POST.dict())
        if self.formset.is_valid() and request.user.is_authenticated():
            #retrieving factterms
            factterm_qs = self.get_queryset()
            factterms = {}
            for factterm in factterm_qs:
                factterms[(factterm.term,factterm.attribute)] = factterm

            #retrieving facttermweights
            facttermweights_qs = FactTermWeight.objects.select_related('fact_term')
            facttermweights = {}
            for facttermweight in facttermweights_qs:
                facttermweights[facttermweight.fact_term.pk] = facttermweight

            for form in self.formset:
                attr_list = form.cleaned_data['fact_term'].split('@')
                assert len(attr_list) > 0 and len(attr_list) < 3, "fact_term not valid"
                if len(attr_list) == 1:
                        factterm = factterms[(attr_list[0],u'')]
                else:
                    factterm = factterms[(attr_list[0],attr_list[1])]
                weight = form.cleaned_data['weight']

                if factterm:
                    if weight:
                        try:
                            facttermweight = facttermweights[factterm.pk]
                            if weight != facttermweight.weight:
                                facttermweight.weight = weight
                                facttermweight.save()
                        except KeyError:
                            facttermweight_new = FactTermWeight(fact_term=factterm,
                                                                weight=weight)
                            facttermweight_new.save()
                    else:
                        try:
                            facttermweight = facttermweights[factterm.pk]
                            facttermweight.delete()
                        except KeyError:
                            continue
        return self.get(request, *args, **kwargs)

class InfoObjectCorrelationView(LoginRequiredMixin, DetailView):
    #TODO list view with correlation
    model = InfoObject
    template_name = 'mantis_malte/%s/details/InfoObjectCorrelation.html' % MANTIS_MALTE_TEMPLATE_FAMILY
    threshold = 0.5

    def get_context_data(self, **kwargs):
        context = super(InfoObjectCorrelationView, self).get_context_data(**kwargs)
        pk = [self.get_object().pk]
        #TODO get_machting_facts annotated graph
        matching_facts = self.get_matching_facts(pk)
        context['cfacts'] = self.get_correlating_iobj(matching_facts,pk)
        return context

    def get_matching_facts(self,pk):
        '''
        retrieving all associated facts which weight is bigger than defined threshold in self.threshold
        '''
        pks_visited = set()
        facts_matching = []

        def get_facts_rec(pks_to_query):
            columns = ['fact__id','fact__value_iobject_id','factterm_set__weight']
            facts_qs = FactTerm.objects.filter(fact__iobject_thru__iobject__in=pks_to_query).distinct('fact__id').values(*columns)
            pks_visited.update(pks_to_query)
            pks_to_visit = set()

            for fact in facts_qs:
                fact_id = fact['fact__id']
                viobj_id = fact['fact__value_iobject_id']
                weight = fact['factterm_set__weight']

                if viobj_id and viobj_id not in pks_visited:
                    pks_to_visit.add(viobj_id)
                else:
                    if weight and weight >= self.threshold:
                        facts_matching.append(fact_id)

            if pks_to_visit:
                return get_facts_rec(pks_to_visit)
            else:
                return facts_matching

        return get_facts_rec(pk)

    def get_correlating_iobj(self, facts, source_pk):
        if facts:
            sr_list = ['fact__fact_term','iobject__name']
            pfr_list = ['fact__fact_values']
            iobj_qs = InfoObject2Fact.objects.filter(fact__in=facts).select_related(*sr_list).prefetch_related(*pfr_list)

            print iobj_qs.query
            return iobj_qs
        else:
            return []



    # def get(self, request, *args, **kwargs):
    #     obj = self.get_object()
    #     obj_pk_list = [obj.pk]
    #     print(obj)
    #     facts = self.get_matching_facts(obj_pk_list)
    #     print(facts)
    #     print(self.get_correlating_iobj(facts,obj_pk_list))
    #     return super(InfoObjectCorrelationView, self).get(request, *args, **kwargs)




