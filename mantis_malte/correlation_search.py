__author__ = 'Philipp Lang'

from dingos.models import InfoObject2Fact, vIO2FValue
from dingos.graph_traversal import follow_references
from dingos.core.utilities import set_dict

from . import DEFAULT_ASSIGNMENT

exclude_facts = [{'term': "Properties/Hashes/Hash/Simple_Hash_Value",
                'attribute': "",
                'value': "d41d8cd98f00b204e9800998ecf8427e"},
                 {'term': "Properties/Hashes/Hash/Simple_Hash_Value",
                  'attribute': "",
                  'value': "da39a3ee5e6b4b0d3255bfef95601890afd80709"},
                 {'term': "Properties/Hashes/Hash/Simple_Hash_Value",
                  'attribute': "",
                'value': "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
                 {'term': "Properties/File_Name",
                  'attribute': "",
                'value': "autoexec.bat"}
                ]

if exclude_facts:
    facts_to_exclude_qs = vIO2FValue.objects.distinct('fact_id').values_list('fact_id', flat=True)
    for fact in exclude_facts:
        facts_to_exclude_qs = facts_to_exclude_qs.filter(term=fact['term'],
                                                        attribute=fact['attribute'],
                                                        value=fact['value'])
    FACTS_TO_EXCLUDE = list(facts_to_exclude_qs)
else:
    FACTS_TO_EXCLUDE = []

def get_matching_io2fvs(pks=None,graph=None,threshold=0.5,assignment=DEFAULT_ASSIGNMENT):
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

    print assignment

    if pks:
        graph_traversal_kargs = {'max_nodes':0,
                                 'direction':'down',
                                 #'keep_graph_info': False,
                                 'iobject_pks': pks}
        G = follow_references(**graph_traversal_kargs)
    else:
        G = graph
    pks = G.nodes()

    io2fvs_of_interest = vIO2FValue.objects.filter(iobject__id__in=G.nodes(),node_id__isnull=False)\
        .filter(factterm__weight_set__weight__gte=threshold,factterm__weight_set__assignment_name__name=assignment)

    #fetch facts to exclude at server startup
    if True:
        io2fvs_of_interest = io2fvs_of_interest.exclude(fact_id__in=FACTS_TO_EXCLUDE)

    #exclude facts per query by filtering
    if False:
        #excluding facts configured in exclude_facts
        for fact in exclude_facts:
            io2fvs_of_interest = io2fvs_of_interest.exclude(term=fact['term'],
                                                            attribute=fact['attribute'],
                                                            value=fact['value'])

    # TODO: probably, below we should add another filter that exclucdes
    # outdated objects (i.e., check that iobject_id = latest_iobject_id) --
    # otherwise we will get matches with older revisions of objects.



    matched_io2fvs = vIO2FValue.objects\
        .filter(fact__in=[x.fact_id for x  in io2fvs_of_interest])\
        .exclude(iobject__in=pks)

    return (io2fvs_of_interest,matched_io2fvs)

