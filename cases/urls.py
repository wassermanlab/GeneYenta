# cases -- urls.py

from django.conf.urls import patterns, url
from cases import views
# from django.core.urlresolvers import reverse


urlpatterns = patterns('',
    
    # ex: inbox/
    url(r'^inbox/$', views.inbox, name='inbox'),

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

)


