from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _

from feinheit import translations
from django.conf import settings
#from feincms.views.generic.list_detail import object_list
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.core.exceptions import ImproperlyConfigured
from feincms.utils.html import cleanse
from feincms.module.medialibrary.models import MediaFile


class Event(models.Model, translations.TranslatedObjectMixin):
    
    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.cleanse = getattr(settings, 'EVENT_CLEANSE', False)
        cm = getattr(settings, 'CLEANSE_MODULE', None)
        if cm:
            try:
                self.cleanse_module = __import__(cm, fromlist=True)
            except (ValueError, ImportError):
                raise ImproperlyConfigured, 'There was an error importing your %s cleanse_module!' % self.__name__        
        else:
            self.cleanse_module = cleanse
    
    datetime = models.DateTimeField(_('Date and Time'), db_index=True)    
    #date = models.DateField(_('date'), default=date.today)
    #time = models.CharField(_('time'), max_length=15, blank=True)
    image = models.ForeignKey(MediaFile, blank=True, null=True)

    class Meta:
        ordering = ['-datetime']
        verbose_name = _('event')
        verbose_name_plural = _('events')

    objects = translations.TranslatedObjectManager()
    

class EventTranslation(translations.Translation(Event)):
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('event translation')
        verbose_name_plural = _('event translations')

    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # TODO: Move this to the form?
        if getattr(self.parent, 'cleanse', False):
            self.description = self.parent.cleanse_module.cleanse_html(self.description)
        super(EventTranslation, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('feinheit.agenda.urls/agenda_event_detail', (), {'slug': self.slug})

class EventsContent(models.Model):

    which = models.CharField(max_length=1, choices=(('u',_('upcoming')),('p',_('past')),))

    class Meta:
        abstract = True
        verbose_name = _('event list')
        verbose_name_plural = _('event lists')

    def render(self, **kwargs):
        request = kwargs.get('request')
        if self.which == 'u':
            object_list = Event.objects.filter(datetime__gte=date.today)
        else:
            object_list = Event.objects.filter(datetime__lte=date.today)
        current_page = request.GET.get('page', 1)  
        page = Paginator(object_list, 20).page(current_page)
        return render_to_string('content/agenda/event_list.html', 
                {'object_list': object_list, 'page': page, },
                context_instance=RequestContext(request))