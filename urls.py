from datetime import date

from django.conf import settings as django_settings
from django.conf.urls.defaults import *

from feinheit.agenda.models import Event
from feinheit.agenda import settings


urlpatterns = patterns('django.views.generic',
    url(r'^(?P<slug>[\w\-]+)/$', 'list_detail.object_detail', {
        'queryset': Event.objects.all(),
        'slug_field': 'translations__slug',
        }, name='agenda_event_detail'),
)



if not settings.AGENDA_USE_CONTENT_TYPE:
    urlpatterns += patterns('django.views.generic',
        url(r'^$', 'list_detail.object_list', {
            'queryset': Event.objects.filter(datetime__gte=date.today),
            'paginate_by': 20,
            }, name='agenda_event_list'),
        url(r'^archive/$', 'list_detail.object_list', {
            'queryset': Event.objects.filter(datetime__lt=date.today),
            'paginate_by': 20,
            }, name='agenda_event_list'),
    )
else:
    def empty(request):return ''
    urlpatterns += patterns('',
        url(r'^$', empty),
)
