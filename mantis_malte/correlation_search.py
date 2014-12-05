__author__ = 'Philipp Lang'

from dingos.models import InfoObject2Fact, vIO2FValue
from dingos.graph_traversal import follow_references
from dingos.core.utilities import set_dict

def get_matching_io2fvs(pks=None,graph=None,threshold=0.5):
    '''
    Given a set of object pks or a complete graph of objects,
    return a dictionary
    retrieving all associated facts with fact-terms associated in
    the model FactTermWeight with a weight that is bigger than defined threshold in
    self.threshold
    '''

    if pks:
        graph_traversal_kargs = {'max_nodes':0,
                                 'direction':'down',
                                 #'keep_graph_info': False,
                                 'iobject_pks': pks}
        G = follow_references(**graph_traversal_kargs)
    else:
        G = graph
        pks = graph.nodes()



    # TODO: The two queries below probably can be made into a single query using
    # a raw query and a join

    io2fvs_of_interest = vIO2FValue.objects.filter(iobject__id__in=G.nodes(),node_id__isnull=False).filter(factterm__factterm_set__weight__gte=threshold)

    matched_io2fvs = vIO2FValue.objects.filter(fact__in=[x.fact_id for x  in io2fvs_of_interest]).exclude(iobject__in=pks)

    return (io2fvs_of_interest,matched_io2fvs)

