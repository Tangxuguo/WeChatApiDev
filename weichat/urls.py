from django.conf.urls import patterns, include, url
from weichat.views import handleRequest
urlpatterns = patterns ('',
                          url(r'^$', handleRequest),
                              
                         )
                  