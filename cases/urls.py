# cases -- urls.py

from django.conf.urls import patterns
from django.conf.urls import url 
from cases import views
# from django.core.urlresolvers import reverse


urlpatterns = patterns('',
    
    # ex: create-case/
    url(r'^create-case/$', views.create_case, name='create_case'),

    # ex: view-cases/
    url(r'^view-cases/$', views.view_cases, name='view_cases'),
    
    url(r'^delete-a-case/(?P<patient_id>\d+)/$', views.delete_patient_matches, name="delete_a_case"),

    # ex: settings/
    url(r'^settings/$', views.settings, name='settings'),

    # ex: 12/patient-detail/
    url(r'^(?P<patient_id>\d+)/patient-detail/$', views.patient_detail, name='patient_detail'),

    # ex: 12/patient-edit/
    url(r'^(?P<patient_id>\d+)/patient-edit/$', views.patient_edit, name='patient_edit'),

    # ex: 12/profile-detail/
    url(r'^(?P<clinician_id>\d+)/profile-edit/$', views.profile_edit, name='profile_edit'),

    # ex: archives/
    url(r'^archives/$', views.archives, name='archives'),

    # ex: change-password/
    url(r'^change-password/$', 'django.contrib.auth.views.password_change', {'template_name':'cases/change-password.html',
    }, name='change_password'),

    # ex: change-password/change-success
    url(r'^change-password/change-success/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'cases/change-password-success.html'},
     name='change_password_success'),

)


