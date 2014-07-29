from django.shortcuts import get_object_or_404, render

from feincms.translations import short_language_code

from .models import Event


def event_list(request, filter):
    if filter == 'upcoming':
        events = Event.objects.upcoming()
    elif filter == 'past':
        events = Event.objects.past()
    else:
        events = Event.objects.active()

    # TODO convert to inheritance 2.0?
    return render(request, 'agenda/event_list.html', {
        'object_list': events,
    })


def event_detail(request, slug):
    event = get_object_or_404(
        Event,
        translations__slug=slug,
        translations__language_code=short_language_code,
    )

    return render(request, 'agenda/event_detail.html', {
        'object': event,
    })
