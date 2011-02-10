from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
## not supported in app engine
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^hello/', include('hello.foo.urls')),
    (r'^', include('meghanurback.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # not supported in app engine
    # (r'^admin/(.*)', admin.site.root),
)
