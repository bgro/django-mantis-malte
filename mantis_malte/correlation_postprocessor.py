from celery.bin.graph import graph

__author__= 'Philipp Lang'

from dingos.graph_traversal import follow_references
from dingos.graph_utils import dfs_preorder_nodes

import networkx as nx

from .correlation_search import get_matching_facts, get_correlating_iobj

def process(graph):
    """
    """
    #TODO enter disription
    corr_graph = nx.MultiDiGraph()
    root = graph.graph['root']
    #TODO config threshold
    threshold = 0.5

    matching_facts = get_matching_facts(graph=graph,threshold=threshold)
    corr_dict = get_correlating_iobj(matching_facts,[root])

    concise_graph = nx.MultiDiGraph()

    concise_graph.add_node(root,attr_dict = graph.node[root])


    for corr_info in corr_dict.values():
        shortest_path = nx.shortest_path(graph,source=root,target=corr_info['iobj_mapping'])
        graph_part = graph.subgraph(shortest_path)
        corr_graph = nx.compose(corr_graph,graph_part)

        concise_graph.add_node(corr_info['iobj_mapping'], graph.node[corr_info['iobj_mapping']])



        for iobj in corr_info['iobjects_embb']:
            correlation_link = {
                'correlation' : True
            }
            corr_graph.add_edge(corr_info['iobj_mapping'],iobj['pk'],**correlation_link)

            kwargs = {
                'iobject_pks' : [iobj['pk']],
                'direction' : 'up',
            }
            #TODO graph building every time neccessary??
            G = follow_references(**kwargs)
            node_ids = list(dfs_preorder_nodes(G, source=iobj['pk']))
            for id in node_ids:
                node = G.node[id]
                # TODO: Below is STIX-specific and should be factored out
                # by making the iobject type configurable
                if "STIX_Package" in node['iobject_type']:
                    current_shortest_path = nx.shortest_path(G.reverse(copy=True),source=id,target=iobj['pk'])
                    current_graph_part = G.subgraph(current_shortest_path)
                    graph_part = nx.compose(graph_part,current_graph_part)
                    corr_graph = nx.compose(corr_graph,graph_part)


    print "postprocessor mantis_malte %s" % (graph)

    return corr_graph
