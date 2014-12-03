__author__= 'Philipp Lang'

from dingos.graph_traversal import derive_image_info

from .views import InfoObjectCorrelationView

def process(graph):
    """
    """
    #TODO enter disription






    print "postprocessor mantis_malte %s" % (graph)

    return InfoObjectCorrelationView.build_correlation_graph(graph)
