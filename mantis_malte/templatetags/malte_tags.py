# Copyright (c) Siemens AG, 2015
#
# This file is part of MANTIS.  MANTIS is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or(at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#


from django import template


from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.utils import html
from django.utils.html import conditional_escape, strip_tags
from django.utils.safestring import mark_safe
from django.conf import settings

from dingos import DINGOS_TEMPLATE_FAMILY

from mantis_malte.models import FactTerm2Weight

from dingos.core import http_helpers
from dingos.core.utilities import get_from_django_obj,get_dict
from dingos.models import BlobStorage

from dingos.graph_traversal import follow_references
from dingos.graph_utils import dfs_preorder_nodes

from dingos.models import InfoObject, InfoObject2Fact, IdentifierNameSpace
from dingos import DINGOS_SEARCH_POSTPROCESSOR_REGISTRY



register = template.Library()


@register.inclusion_tag('mantis_malte/%s/includes/_CorrelationSchemaDisplay.html'% DINGOS_TEMPLATE_FAMILY,takes_context=True)
def show_CorrelationSchema(context,
                           assignment_name):
    threshold = context['view'].threshold
    columns = ['fact_term__term','fact_term__attribute','weight']
    fact_terms = FactTerm2Weight.objects.filter(assignment_name__name = assignment_name,weight__gte=threshold).select_related('fact_term').values(*columns)
    fact_term_list = []
    for fact_term in fact_terms:
        fact_term_list.append(
        ("%s@%s" % (fact_term['fact_term__term'], fact_term['fact_term__attribute']) if fact_term['fact_term__attribute'] else "%s" % (fact_term['fact_term__term']),
        fact_term['weight'])
        )
    fact_term_list.sort()
    return {'fact_terms':fact_term_list,
        }