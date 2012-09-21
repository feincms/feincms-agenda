from django.conf.urls.defaults import *

from feinheit.agenda.models import Event

from api import events


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
        }, name='agenda_archive_list'),
    
    url(r'^filter/(?P<year>\d{4})/$', 'django.views.generic.date_based.archive_year', {
        'queryset' : Event.objects.active(),
        'date_field' : 'start_date',
        'allow_future' : True,
        'make_object_list' : True,
        'template_name' : 'agenda/event_list.html',
        }, name="agenda_year_list"),
    url(r'^filter/(?P<year>\d{4})/(?P<month>\d{2})/$', 'django.views.generic.date_based.archive_month', {
        'queryset' : Event.objects.active(),
        'month_format' : '%m',
        'date_field' : 'start_date',
        'allow_future' : True,
        'template_name' : 'agenda/event_list.html',
        }, name="agenda_month_list"),
    
    url('^api/events/', events, name='agenda_api_events'),
)