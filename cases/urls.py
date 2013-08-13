# cases -- urls.py

from django.conf.urls import patterns, url
from cases import views
# from django.core.urlresolvers import reverse


urlpatterns = patterns('',
    
    # ex: view_matches/
    url(r'^view-matches/$', views.view_matches, name='view_matches'),

    # ex: create-case/
    url(r'^create-case/$', views.create_case, name='create_case'),

    # ex: view-cases/
    url(r'^view-cases/$', views.view_cases, name='view_cases'),

    # ex: matches/
    url(r'^matches/$', views.matches, name='matches'),

    # ex: settings/
    url(r'^settings/$', views.settings, name='settings'),

    # ex: 12/patient-detail/
    url(r'^(?P<patient_id>\d+)/patient-detail/$', views.patient_detail, name='patient_detail'),

    # ex: 12/patient-edit/
    url(r'^(?P<patient_id>\d+)/patient-edit/$', views.patient_edit, name='patient_edit'),

    # ex: 12/phenotype-edit/
    # url(r'^(?P<patient_id>\d+)/phenotype-edit/$', views.phenotype_edit, name='phenotype_edit'),

    # ex: 12/profile-detail/
    url(r'^(?P<clinician_id>\d+)/profile-edit/$', views.profile_edit, name='profile_edit'),

    # ex: 12/match-detail/
    url(r'^(?P<match_id>\d+)/match-detail/$', views.match_detail, name='match_detail'),

    url(r'^archives/$', views.archives, name='archives'),

    url(r'^change-password/$', 'django.contrib.auth.views.password_change', {'template_name':'cases/change-password.html',
    }, name='change_password'),

    url(r'^change-password/change-success/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'cases/change-password-success.html'},
     name='change_password_success'),

)


