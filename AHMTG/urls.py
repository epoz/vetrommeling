from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'AHMTG.views.home', name='home'),
    url(r'^tagexports/$', 'AHMTG.views.tagexports'),
    url(r'^help/(.*)', 'AHMTG.views.help', name='help'),
    url(r'^adlibpreview/$', 'AHMTG.views.adlibpreview', name='adlibpreview'),
    url(r'^makeseries/$', 'AHMTG.views.makeseries', name='makeseries'),
    url(r'^makepybossa/$', 'AHMTG.views.makepybossa', name='makepybossa'),
    url(r'^doseries/(\d+)/$', 'AHMTG.views.doseries', name='makeseries'),
    url(r'^answer/$', 'AHMTG.views.save_answer', name='answer'),

    url(r'^login/$', 'AHMTG.views.loginmethod', name="login"),
    url(r'^logout/$', 'AHMTG.views.logoutmethod', name="logout"),
    url(r'^register/$', 'AHMTG.views.registermethod', name="register"),

    url(r'^admin/', include(admin.site.urls)),
)
