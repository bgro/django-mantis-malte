__author__ = 'Philipp Lang'

from dingos.models import InfoObject2Fact, vIO2FValue
from dingos.graph_traversal import follow_references
from dingos.core.utilities import set_dict

def get_matching_io2fvs(pks=None,graph=None,threshold=0.5):
    '''
    Given a set of iobject primary keys (which are then
    expanded into a downwward-reachability graph) or a
    already calculated graph, this function does the following:

    - from all objects in the graph, it extracts the
      facts (as io2fv objects) whose fact term has been
      weighed with a value larger than the threshold.

      These are the io2fv of interest: we are interested
      into io2fv occuring in other objects that are matching
      in the sense that they contain the same fact

    - extracting the facts found in the io2fvs of interest,
      the function extracts all io2fv objects *not* already
      found in this graph (determiend by the iobject with
      which they are assoicated). These are the matching
      io2fv

    Both sets of io2fv are returned.

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

    io2fvs_of_interest = vIO2FValue.objects.filter(iobject__id__in=G.nodes(),node_id__isnull=False)\
        .filter(factterm__factterm_set__weight__gte=threshold)

    # TODO: probably, below we should add another filter that exclucdes
    # outdated objects (i.e., check that iobject_id = latest_iobject_id) --
    # otherwise we will get matches with older revisions of objects.

    matched_io2fvs = vIO2FValue.objects\
        .filter(fact__in=[x.fact_id for x  in io2fvs_of_interest])\
        .exclude(iobject__in=pks)

    return (io2fvs_of_interest,matched_io2fvs)

