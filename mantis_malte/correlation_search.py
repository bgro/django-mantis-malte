__author__ = 'Philipp Lang'

from dingos.models import InfoObject2Fact, vIO2FValue
from dingos.graph_traversal import follow_references

def get_matching_facts(pk,threshold):
    '''
    retrieving all associated facts which weight is bigger than defined threshold in self.threshold
    '''
    graph_traversal_kargs = {'max_nodes':0,
                             'direction':'down',
                             #'keep_graph_info': False,
                             'iobject_pks': pk}
    G = follow_references(**graph_traversal_kargs)
    pfr_list = []
    io2fvs= vIO2FValue.objects.filter(iobject__id__in=G.nodes(),node_id__isnull=False).prefetch_related(*pfr_list).filter(factterm__factterm_set__weight__gte=threshold)
    facts_matching = dict([(x.fact_id,x.iobject_id) for x in io2fvs])
    return facts_matching

def get_correlating_iobj(facts, source_pk):
    if facts:
        sr_list = ['fact__fact_term','iobject__name']
        #TODO prefetching fact_values not working correct, leads to multiple querying per fact
        pfr_list = ['fact__fact_values']
        iobj_qs = InfoObject2Fact.objects.filter(fact__in=facts.keys()).exclude(iobject__in=source_pk).select_related(*sr_list).prefetch_related(*pfr_list)
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
