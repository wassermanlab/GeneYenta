# cases -- urls.py

from django.conf.urls import patterns, url
from matches import views
# from django.core.urlresolvers import reverse


urlpatterns = patterns('',
    
    # ex: view_matches/
    url(r'^view-matches/$', views.view_matches, name='view_matches'),
	
	# ex: matches/
    url(r'^matches/$', views.matches, name='matches'),
	
	# ex: 12/match-detail/
    url(r'^(?P<match_id>\d+)/match-detail/$', views.match_detail, name='match_detail'),




)