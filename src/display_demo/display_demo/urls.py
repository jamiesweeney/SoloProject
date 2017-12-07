from django.conf.urls import patterns, url
from django.conf.urls import include
from django.contrib import admin
from display import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tango_with_django_project_17.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^display/', include('display.urls')), # ADD THIS NEW TUPLE!
)
