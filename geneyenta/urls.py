from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'geneyenta.views.home', name='home'),
    # url(r'^geneyenta/', include('geneyenta.foo.urls')),
    # url(r'^login/', include('registration.urls')),

    url(r'^gy3/', include ('registration.urls')),
    url(r'^gy3/accounts/', include('registration.urls')),
    url(r'^gy3/cases/', include('cases.urls')),

    # url(r'^registration/', include('registration.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns += staticfiles_urlpatterns()
