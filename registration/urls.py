# registration -- urls.py

from django.conf.urls import patterns, url
from registration import views
# from django.core.urlresolvers import reverse


urlpatterns = patterns('',
	
    url(r'^$', views.home_redirect, name='home_redirect'),

    # ex: gy3/login/login-success/
    url(r'^login/login-success/$', views.login_success, name='login-success'),

    # ex: gy3/login/
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'registration/login.html',
       'extra_context': 
       {
       'next':'login-success/'
       },									}, name='home'),
    
    # ex: gy3/registration/registration-success/
    url(r'^registration/registration-success/$', views.registration_success, name='registration-success'),

    # ex: gy3/login/registration/
    url(r'^registration/$', views.registration, name='registration'),

    # ex: gy3/change-password/change-success/
    url(r'^change-password/change-success/$', views.change_success, name='change_success'),

    # ex: gy3/change-password/
    url(r'^change-password/$', 'django.contrib.auth.views.password_change', 
        {'template_name':'registration/password-change.html',
        'post_change_redirect':'change-success/',
        }),
    

    # ex: gy3/logout/
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page':'logout-success/'}),

    # ex: gy3/logout/logout-success/
    url(r'^logout/logout-success/$', views.logout_redirect, name='login-redirect'),


# The following 3 url configs seem to work; but use the default admin templates
# Requires proper set up of STMP mail servers
# (r'^password_reset/$', 'django.contrib.auth.views.password_reset'),
# (r'^password_reset_done/$', 'django.contrib.auth.views.password_reset_done'),
# (r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),


# These urls don't really work very well.
# url(r'^forgot-password/confirm/(?P<uidb36>\d+)/(?P<token>[\d\w-]+)$', 'django.contrib.auth.views.password_reset_confirm', {'template_name':'registration/change-success.html',      
# #     }),

# url(r'^forgot-password/done$', 'django.contrib.auth.views.password_reset_done', {'template_name':'registration/change-success.html',      
#     }),

# url(r'^forgot-password/$', 'django.contrib.auth.views.password_reset', {'template_name':'registration/forgot-password.html',      
#     'from_email':'jimbean2020@gmail.com',
#     'email_template_name':'registration/password-reset-email.html',
#     'post_reset_redirect':'change-success',
#     'from_email':'jimbean2020@gmail.com'
#     }),

)
