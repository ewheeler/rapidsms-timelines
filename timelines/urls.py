from __future__ import unicode_literals

from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^$',
        views.OccurrenceList.as_view(),
        name='occurrence_list',
    ),
    url(r'^csv/$',
        views.CSVOccurrenceList.as_view(),
        name='csv_occurrence_list',
    ),
    url(r'^filter/$', views.subscriptionsView, name='subscriptions-view'),
    url(r'^performance/$', views.performanceView, name='performance-view'),
    url(r'^export/$', views.performanceExcelView, name='performance-excel'),
)
