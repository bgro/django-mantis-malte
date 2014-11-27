__author__ = 'Philipp Lang'

from django.conf.urls import patterns, url

from mantis_malte import views

urlpatterns = patterns('',

    #TODO Correlation View for single Infobject
    url(r'^View/Correlation/(?P<pk>\d*)$',
        views.FactTermWeightEdit.as_view(),
        name="url.dingos.list.infoobject.generic"),

    url(r'^View/Correlation/Config/$',
        views.FactTermWeightEdit.as_view(),
        name="url.mantis_malte.corr.config"),
    )


