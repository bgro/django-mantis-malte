__author__ = 'Philipp Lang'

from dingos.models import InfoObject2Fact, vIO2FValue
from dingos.graph_traversal import follow_references
from dingos.core.utilities import set_dict

def get_matching_facts(pks=None,graph=None,threshold=0.5):
    '''
    Given a set of object pks or a complete graph of objects,
    return a dictionary
    retrieving all associated facts which weight is bigger than defined threshold in self.threshold
    '''

    if pks:
        graph_traversal_kargs = {'max_nodes':0,
                                 'direction':'down',
                                 #'keep_graph_info': False,
                                 'iobject_pks': pks}
        G = follow_references(**graph_traversal_kargs)
    else:
        G = graph

    pfr_list = []
    io2fvs= vIO2FValue.objects.filter(iobject__id__in=G.nodes(),node_id__isnull=False).prefetch_related(*pfr_list).filter(factterm__factterm_set__weight__gte=threshold)

    result_dict = {}

    for io2fv in io2fvs:
        set_dict(result_dict,io2fv.iobject_id,'append',io2fv.fact_id)

    return result_dict

def get_correlating_iobj(entry2iobj, source_pks):
    correlated_io2fvs = vIO2FValue.objects.filter(fact__in=entry2iobj.keys()).exclude(iobject__in=source_pks)

    return correlated_io2fvs

    corr_dict = {}
    for correlated_io2fv in correlated_io2fvs:
        #res_dict = {}'term': correlated_io2fv. = corr.fact.fact_term
        #        corr_fact['values'] = corr.fact.fact_values.values_list('value',flat=True)
        #        corr_fact['iobj_mapping'] = facts[corr.fact_id]
        #        corr_fact['iobjects_embb'] = [{
        #            'pk' : corr.iobject.pk,
        #            'name' : corr.iobject.name,
        #            'root' : "testRoot",
        #            'root_pk' : 48
        #        }
        set_dict(corr_dict,'set',correlated_io2fv.value,correlated_io2fv.iobject_id)
        set_dict(corr_dict,'append',correlated_io2fv.value,correlated_io2fv.iobject_id)

    if facts:
        sr_list = ['fact__fact_term','iobject__name']
        #TODO prefetching fact_values not working correct, leads to multiple querying per fact
        pfr_list = ['fact__fact_values']
        #iobj_qs = InfoObject2Fact.objects.filter(fact__in=facts.keys()).exclude(iobject__in=source_pk).select_related(*sr_list).prefetch_related(*pfr_list)

        corr_dict = {}
        for corr in iobj_qs:
            try:
                corr_fact = corr_dict[corr.fact_id]
                corr_fact['iobjects_embb'].append({
                    'pk' : corr.iobject.pk,
                    'name' : corr.iobject.name,
                    'root' : "testRoot",
                    'root_pk' : 48
                })

            except KeyError:
                corr_fact = {}
                corr_fact['term'] = corr.fact.fact_term
                corr_fact['values'] = corr.fact.fact_values.values_list('value',flat=True)
                corr_fact['iobj_mapping'] = facts[corr.fact_id]
                corr_fact['iobjects_embb'] = [{
                    'pk' : corr.iobject.pk,
                    'name' : corr.iobject.name,
                    'root' : "testRoot",
                    'root_pk' : 48
                }]
                corr_dict[corr.fact_id] = corr_fact
        return corr_dict
    else:
        return []
