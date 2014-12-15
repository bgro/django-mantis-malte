__author__ = 'Philipp Lang'

from braces.views import LoginRequiredMixin

from collections import OrderedDict

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms.formsets import formset_factory
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from dingos.models import FactTerm, InfoObject
from dingos.core.utilities import set_dict

from dingos.templatetags.dingos_tags import reachable_packages

from dingos.view_classes import ViewMethodMixin, CommonContextMixin
from . import MANTIS_MALTE_TEMPLATE_FAMILY, ELEMENTS_PER_PAGE, DEFAULT_ASSIGNMENT
from .forms import FactTermCorrelationEditForm, CorrelationViewForm
from .models import FactTerm2Weight, AssignmentName
from .correlation_search import get_matching_io2fvs



class FactTermWeightEdit(LoginRequiredMixin, ViewMethodMixin, ListView):

    # make sure that the default assignment exists
    AssignmentName.objects.get_or_create(name=DEFAULT_ASSIGNMENT)

    model = FactTerm

    template_name = 'mantis_malte/%s/edits/FactTermWeightEdit.html' % MANTIS_MALTE_TEMPLATE_FAMILY

    form_class = formset_factory(FactTermCorrelationEditForm, extra=0)
    formset = None



    #TODO set title
    title = 'Title Test'

    def get_context_data(self, **kwargs):
        context = super(FactTermWeightEdit, self).get_context_data(**kwargs)
        context['formset'] = self.formset
        context['factterms'] = self.fact_terms
        context['paginator'] = self.factterms_paginator
        context['page_obj'] = self.factterms
        return context

    def get(self, request, *args, **kwargs):
        initial = []
        self.page = request.GET.get('page')

        columns = ['id','term','attribute','weight_set__assignment_name__name','weight_set__weight']

        factterm_list = self.get_queryset().values(*columns).order_by('term')
        self.factterms_paginator = Paginator(factterm_list, ELEMENTS_PER_PAGE)

        if self.factterms_paginator.num_pages == 1:
            self.is_paginated = False
        else:
            self.is_paginated = True

        try:
            self.factterms = self.factterms_paginator.page(self.page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            self.factterms = self.factterms_paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            self.factterms = self.factterms_paginator.page(self.factterms_paginator.num_pages)

        self.fact_terms = OrderedDict()
        for fact_term in self.factterms:
            curr_factterm = self.fact_terms.get(fact_term['id'],False)
            if curr_factterm:
                curr_factterm['weights'].append("%s: %s" % (fact_term['weight_set__assignment_name__name'],fact_term['weight_set__weight']))
            else:
                self.fact_terms[fact_term['id']] = {
                'term' : "%s@%s" % (fact_term['term'], fact_term['attribute']) if fact_term['attribute'] else "%s" % (fact_term['term']),
                'weights' : ["%s: %s" % (fact_term['weight_set__assignment_name__name'],fact_term['weight_set__weight'])]
                }
        for factterm_id in self.fact_terms.keys():
            initial.append({
                'factterm' : factterm_id
            })

        self.formset = self.form_class(initial=initial)

        return super(FactTermWeightEdit, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.formset = self.form_class(request.POST.dict())
        if self.formset.is_valid() and request.user.is_authenticated():

            #retrieving facttermweights
            facttermweights_qs = FactTerm2Weight.objects.select_related('fact_term')
            facttermweights = {}
            for facttermweight in facttermweights_qs:
                facttermweights[(facttermweight.fact_term.pk,facttermweight.assignment_name.pk)] = facttermweight

            for form in self.formset:
                if form.cleaned_data:
                    factterm = form.cleaned_data['factterm']
                    weight = form.cleaned_data['weight']
                    assignment = form.cleaned_data['assignment_name']
                    if assignment:
                        if weight:
                            try:
                                facttermweight = facttermweights[(factterm.pk,assignment.pk)]
                                if weight != facttermweight.weight:
                                    facttermweight.weight = weight
                                    facttermweight.save()
                            except KeyError:
                                facttermweight_new = FactTerm2Weight(fact_term=factterm,
                                                                     assignment_name=assignment,
                                                                     weight=weight)
                                facttermweight_new.save()
                        else:
                            try:
                                facttermweight = facttermweights[(factterm.pk,assignment.pk)]
                                facttermweight.delete()
                            except KeyError:
                                continue
            #TODO catch invalid form, e.g. weight out of range
        return self.get(request, *args, **kwargs)

class InfoObjectCorrelationView(CommonContextMixin, ViewMethodMixin, LoginRequiredMixin, DetailView):
    #TODO list view with correlation
    model = InfoObject
    template_name = 'mantis_malte/%s/details/InfoObjectCorrelation.html' % MANTIS_MALTE_TEMPLATE_FAMILY
    threshold = 0.5
    #default value
    assignment,dummy = AssignmentName.objects.get_or_create(name=DEFAULT_ASSIGNMENT)


    def get_context_data(self, **kwargs):
        context = super(InfoObjectCorrelationView, self).get_context_data(**kwargs)
        pks = [self.get_object().pk]

        io2fvs_of_interest, matching_io2fvs = get_matching_io2fvs(pks=pks,threshold=self.threshold,assignment=self.assignment.name)

        self.matching_io2fvs = matching_io2fvs

        context['matching_io2fvs'] = self.matching_io2fvs


        # The dictionaries below are populated such that
        # they allow us to retrieve required information
        # fast in the view.


        # Mapping of fact_id to list of io2vf-of-interest-objects containing that fact_id
        fact_id__2__io2vf_oi ={}

        # Mapping of iobject_id to list of io2vf-of-interest-objects containing that fact_id
        iobject_id__2__io2vf_oi = {}

        # The same as the two above, but for the macthing io2vf-objects
        fact_id__2__matching_io2vf ={}
        iobject_id__2__matching_io2v = {}

        # Mapping of iobject_id of matching Info-Objects to information
        # about the found top-level object pks,

        matching_iobject_id__2__top_level_object_ids = {}

        # Mapping from top-level iobject pks to the referenced matching iobjects

        top_level_iobject_id__2__matching_obj_ids = {}

        # Mapping of top-level iobject pk to associated node info from graph representation

        top_level_iobject_id__2__node_info = {}

        for io2fv in io2fvs_of_interest:
            # The set_dict function is a concise notation for
            # inserting stuff into a hierarchical dictionary.
            # The call below takes the fact_id__2__io2vf_oi dictionary
            # and appends each io2fv to a list of io2fvs
            # associated with the pk of the contained fact_id (if the key fact_id
            # does not exist already, a singleton list is created
            # automatically.

            set_dict(fact_id__2__io2vf_oi,io2fv,'append',io2fv.fact_id)

            set_dict(iobject_id__2__io2vf_oi, io2fv, 'append',io2fv.iobject_id)

        for io2fv in matching_io2fvs:

            set_dict(fact_id__2__matching_io2vf,io2fv,'append',io2fv.fact_id)

            set_dict(iobject_id__2__matching_io2v, io2fv, 'append',io2fv.iobject_id)


        for matching_io2fv in matching_io2fvs:
            matching_io2fv.objects_oi = fact_id__2__io2vf_oi[matching_io2fv.fact_id]


        # We need to set the object_list in order for the
        # template tag 'reachable_packages' to work

        context['object_list'] = [x.iobject_id for x in context['matching_io2fvs']]



        for matched_object_pk in context['object_list']:
            found_top_level_objects = reachable_packages(context,matched_object_pk)['node_list']
            for (pk,node_info) in found_top_level_objects:
                set_dict(matching_iobject_id__2__top_level_object_ids,pk,'add_elt',matched_object_pk)
                top_level_iobject_id__2__node_info[pk] = node_info
                set_dict(top_level_iobject_id__2__matching_obj_ids,matched_object_pk,'add_elt',pk)


        context['form'] = CorrelationViewForm(initial={'assignment_name' : self.assignment})


        context["fact_id__2__io2vf_oi"] = fact_id__2__io2vf_oi

        context["iobject_id__2__io2vf_oi"] = iobject_id__2__io2vf_oi

        context["fact_id__2__matching_io2vf"] = fact_id__2__matching_io2vf

        context["iobject_id__2__matching_io2v"] = iobject_id__2__matching_io2v

        context["matching_iobject_id__2__top_level_object_ids"] = matching_iobject_id__2__top_level_object_ids

        context["top_level_iobject_id__2__matching_obj_ids"] = top_level_iobject_id__2__matching_obj_ids

        context["top_level_iobject_id__2__node_info"] = top_level_iobject_id__2__node_info


        return context

    def post(self, request, *args, **kwargs):
        form = CorrelationViewForm(request.POST)
        if form.is_valid():
            self.assignment, dummy = AssignmentName.objects.get_or_create(name=form.cleaned_data['assignment_name'])
        return super(InfoObjectCorrelationView, self).get(request, *args, **kwargs)
