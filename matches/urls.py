# matches -- urls.py

from django.conf.urls import patterns, url
from matches import views
# from django.core.urlresolvers import reverse


urlpatterns = patterns('',
    
    # ex: view_matches/
    url(r'^view-matches/$', views.view_matches, name='view_matches'),
    url(r'^view-matches/(?P<patient_id>.+)/(?P<scroll_pixel>\d+)/$', views.view_matches),
	
	# ex: 12/match-detail/
    url(r'^(?P<match_id>\d+)/match-detail/$', views.match_detail, name='match_detail'),
    url(r'^(?P<match_id>\d+)/match-detail/(?P<patient_id>\d+)/$', views.match_detail),
    url(r'^(?P<match_id>\d+)/match-detail/(?P<patient_id>.+)/(?P<scroll_pixel>\d+)/$', views.match_detail),
    #url(r'^(?P<match_id>\d+)/match-detail/(?P<id>\w+)/(?P<scrollPixel>\w+)$', views.match_detail, name='match_detail'),

)
