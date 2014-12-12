__author__ = 'Philipp Lang'

from django.conf.urls import patterns, url

from mantis_malte import views

urlpatterns = patterns('',

    url(r'^View/Correlation/(?P<pk>\d*)$',
        views.InfoObjectCorrelationView.as_view(),
        name="url.mantis_malte.view.corr.infoobject"),

    url(r'^View/Correlation/Config/$',
        views.FactTermWeightEdit.as_view(),
        name="url.mantis_malte.view.corr.config"),
    )


