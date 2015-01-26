__author__ = 'Philipp Lang'

from django.conf.urls import patterns, url

from mantis_malte import views

urlpatterns = patterns('',

    url(r'^View/InfoObject/(?P<pk>\d*)/correlation/(?P<assignment_name>[a-zA-Z0-9_]+)?/?$',
        views.InfoObjectCorrelationView.as_view(),
        name="url.mantis_malte.view.corr.infoobject"),

    url(r'^Admin/CorrelationWeights/(?P<assignment_name>[a-zA-Z0-9_]+)?/?$',
        views.FactTermWeightEdit.as_view(),
        name="url.mantis_malte.view.corr.config"),
    )


