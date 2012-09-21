from django.shortcuts import get_object_or_404
from django.template.context import RequestContext
from django.template.loader import render_to_string

from feincms.translations import short_language_code

from models import Event


def event_list(request, filter):
    if filter == 'upcoming':
        events = Event.objects.upcoming()
    elif filter == 'past':
        events = Event.objects.past()
    else:
        events = Event.objects.active()
    
    return render_to_string('agenda/event_list.html', {'object_list' : events}, RequestContext(request))

def event_detail(request, slug):
    event = get_object_or_404(Event, translations__slug=slug, translations__language_code=short_language_code)
    
    return render_to_string('agenda/event_detail.html', {'object' : event}, RequestContext(request))