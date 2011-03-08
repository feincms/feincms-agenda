from datetime import date

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
            'queryset': Event.objects.filter(date__gte=date.today),
            'paginate_by': 20,
            }, name='agenda_event_list'),
        url(r'^archive/$', 'list_detail.object_list', {
            'queryset': Event.objects.filter(date__lte=date.today),
            'paginate_by': 20,
            }, name='agenda_event_list'),
    )
else:
    def empty(request):return ''
    urlpatterns += patterns('',
        url(r'^$', empty),
)
