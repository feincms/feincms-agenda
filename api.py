from django.core import serializers
from django.http import HttpResponse

from feincms.views.decorators import standalone

from models import Event

@standalone
def events(request):
    filter = request.REQUEST.get('filter', 'upcoming')
    
    if filter == 'past':
        events = Event.objects.past()
    elif filter == 'active':
        events = Event.objects.active()
    elif filter == 'all':
        events = Event.objects.all()
    else:
        events = Event.objects.upcoming()
        
    return HttpResponse(serializers.serialize('json', events, ensure_ascii=False), mimetype="text/javascript")