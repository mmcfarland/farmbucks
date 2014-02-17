from django.conf.urls import patterns, include, url
from django.contrib import admin
from ledger.views import *

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', route(GET=home)),
    url(r'^(?P<merchant>\w+)/(?P<username>\w+)/status/$', route(GET=account_status)),
    url(r'^(?P<merchant>\w+)/sale/$', 
        route(GET=merchant_transaction, POST=make_sale)),
    url(r'^(?P<merchant>\w+)/sale/(?P<transaction_id>\d+)/$', route(GET=sale_detail)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls'))
)
