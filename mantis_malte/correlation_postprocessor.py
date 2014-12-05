from celery.bin.graph import graph

__author__= 'Philipp Lang'

from dingos.graph_traversal import follow_references
from dingos.graph_utils import dfs_preorder_nodes
from dingos.core.utilities import set_dict

import networkx as nx

from .correlation_search import get_matching_io2fvs

def process(graph):
    """
    """
    #TODO enter disription

    root = graph.graph['root']
    #TODO config threshold
    threshold = 0.5


    io2fvs_of_interest, matching_io2fvs = get_matching_io2fvs(pks=[root],threshold=threshold)

    fact2obj ={}

    source_obj_set = set()

    for io2fv in io2fvs_of_interest:

        set_dict(fact2obj,io2fv.iobject_id,'append',io2fv.fact_id)
        source_obj_set.add(io2fv.iobject_id)




    matched_objects = [x.iobject_id for x in matching_io2fvs]

    corr_graph = follow_references(matched_objects, direction= 'up',reverse_direction=True)

    concise_graph = nx.MultiDiGraph()

    concise_graph.add_node(root,attr_dict = graph.node[root])
    for source_obj in source_obj_set:
        concise_graph.add_node(source_obj,attr_dict = graph.node[source_obj])
        concise_graph.add_edge(root,source_obj)

        shortest_path = nx.shortest_path(graph,source=root,target=source_obj)
        graph_part = graph.subgraph(shortest_path)
        corr_graph = nx.compose(corr_graph,graph_part)

    for io2fv in matching_io2fvs:
        concise_graph.add_node(io2fv.iobject_id,attr_dict=corr_graph.node[io2fv.iobject_id])

        for source_obj in fact2obj[io2fv.fact_id]:
            corr_graph.add_edge(source_obj,io2fv.iobject_id,correlation=True)
            concise_graph.add_edge(source_obj,io2fv.iobject_id,correlation=True)


            node_ids = list(dfs_preorder_nodes(corr_graph.reverse(), source=io2fv.iobject_id))
            for id in node_ids:
                node = corr_graph.node[id]
                if "STIX_Package" in node['iobject_type']:
                    concise_graph.add_node(id,attr_dict = corr_graph.node[id])
                    concise_graph.add_edge(id,io2fv.iobject_id)

    print "Corr Graph %s" % len(corr_graph.nodes())
    print "Concsie graph %s" % len(concise_graph.nodes())

    return concise_graph
