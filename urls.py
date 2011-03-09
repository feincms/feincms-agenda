from django.conf.urls.defaults import *

from feinheit.agenda.models import Event


urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list', {
        'queryset': Event.objects.upcoming(),
        'paginate_by': 20,
        }, name='agenda_event_list'),
    url(r'^(?P<slug>[\w-]+)/$', 'django.views.generic.list_detail.object_detail', {
        'queryset': Event.objects.all(),
        'slug_field': 'translations__slug',
        }, name='agenda_event_detail'),
    url(r'^archive/$', 'django.views.generic.list_detail.object_list', {
        'queryset': Event.objects.past(),
        'paginate_by': 20,
        }, name='agenda_event_list'),
)
