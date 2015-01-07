from celery.bin.graph import graph

__author__= 'Philipp Lang'

from dingos.graph_traversal import follow_references
from dingos.graph_utils import dfs_preorder_nodes
from dingos.core.utilities import set_dict

from mantis_stix_importer.graph_postprocessors import standard_postprocessor as stix_standard_postprocessor

import networkx as nx

from . import DEFAULT_ASSIGNMENT
from .correlation_search import get_matching_io2fvs

MAX_DISPLAY_NODES = 200

def process(graph,**kwargs):
    """
    Given a graph, calculate a graph showing correlation information.

    The function calculates three graphs and returns the graph
    whose size is displayable:

    - corr_graph
      A graph that prunes the given
      graph by extracting the paths from the root object to all objects
      for which a match was found and adds to that all matching objects
      (and their upward reachability)

    - concise_graph

      A graph containing only the links between root node and objects
      of interests, the edges symbolizing the found match, and
      the matched objects with a link to the top-level objects
      (STIX packages or whatever) in which they are contained.

    - very_concise_graph (TODO):

      A graph that only contains the root object and top-level objeccts
      (STIX packages or whatever) referencing the matched objects.
    """

    print kwargs

    unfolding = kwargs.get('unfolding','auto')

    root = graph.graph['root']
    
    threshold = 0.5


    # Below we calculate the following:
    # - io2fvs_of_interest:
    #   From all objects in the graph, the
    #   facts (as io2fv objects) whose fact term has been
    #   weighed with a value larger than the threshold.
    #  
    #   These are the io2fv of interest: we are interested
    #   into io2fv occuring in other objects that are matching
    #   in the sense that they contain the same fact
    #  
    # - matching_io2vs:
    #   All io2fv objects *not* already
    #   found in this graph (determined by the iobject with
    #   which they are assoicated) containing a fact that is
    #   contained in at least one of the io2fvs_of_interest. 
    #   These are the matching io2fv.

    io2fvs_of_interest, matching_io2fvs = get_matching_io2fvs(graph=graph,threshold=threshold,assignment=DEFAULT_ASSIGNMENT)


    # We will compile a dictionary matching facts to the iobjects of interest
    # in which the fact occured
    
    fact2obj ={}

    # We also extract all objects of interest, i.e., objects in the original
    # graph containing a fact of interest
    
    obj_of_interest = set()

    for io2fv in io2fvs_of_interest:
        # The set_dict function is a concise notation for
        # inserting stuff into a hierarchical dictionary.
        # The call below takes the fact2obj dictionary
        # and appends the io2fv.iobject_id to a list of objects
        # associated with the key fact_id (if the key fact_id
        # does not exist already, a singleton list is created
        # automatically.
        
        set_dict(fact2obj,io2fv.iobject_id,'append',io2fv.fact_id)
        obj_of_interest.add(io2fv.iobject_id)

    # We extracted the matched objects
    matched_objects = [x.iobject_id for x in matching_io2fvs]


    # We seed the corr_graph with the upward reachability closure of
    # all matched objects

    corr_graph = follow_references(matched_objects, direction= 'up',reverse_direction=True)

    # Later, we will need exactly that graph for looking up the top-level
    # objects, so we create a copy (we need to reverse it because we must follow
    # the relations from referenced objects to referencing objects

    reachability_graph =  corr_graph.reverse()

    concise_graph = nx.DiGraph()
    concise_graph.add_node(root,attr_dict = graph.node[root])
    very_concise_graph = nx.DiGraph()
    very_concise_graph.add_node(root,attr_dict = graph.node[root])


    for source_obj in obj_of_interest:

        shortest_path = nx.shortest_path(graph,source=root,target=source_obj)
        graph_part = graph.subgraph(shortest_path)
        corr_graph = nx.compose(corr_graph,graph_part)

    for io2fv in matching_io2fvs:
        concise_graph.add_node(io2fv.iobject_id,attr_dict=corr_graph.node[io2fv.iobject_id])

        for source_obj in fact2obj[io2fv.fact_id]:
            corr_graph.add_edge(source_obj,io2fv.iobject_id,correlation=True)

            concise_graph.add_node(source_obj,attr_dict = graph.node[source_obj])
            concise_graph.add_edge(root,source_obj)

            concise_graph.add_edge(source_obj,io2fv.iobject_id,correlation=True)


            node_ids = list(dfs_preorder_nodes(reachability_graph, source=io2fv.iobject_id))

            for id in node_ids:
                node = corr_graph.node[id]
                #if "STIX_Package" in node['iobject_type']:
                if (len(very_concise_graph.nodes()) < MAX_DISPLAY_NODES and
                                node['iobject_type'] in ["Indicator", "STIX_Package"]):
                    concise_graph.add_node(id,attr_dict = reachability_graph.node[id])
                    concise_graph.add_edge(id,io2fv.iobject_id)

                    very_concise_graph.add_node(id,attr_dict = reachability_graph.node[id])
                    very_concise_graph.add_edge(root,id,correlation=True)


    corr_graph = stix_standard_postprocessor.process(corr_graph)

    if len(very_concise_graph.nodes()) < MAX_DISPLAY_NODES:
        very_concise_graph.graph['max_nodes_reached']= MAX_DISPLAY_NODES


    if unfolding in ['full','auto'] and len(corr_graph.nodes()) < MAX_DISPLAY_NODES:
        return corr_graph
    elif unfolding in ['concise','auto'] and len(concise_graph.nodes()) < MAX_DISPLAY_NODES:
        return concise_graph
    else:
        return very_concise_graph


