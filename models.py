from datetime import date, datetime, timedelta, time

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.paginator import Paginator
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from feincms.utils.html import cleanse
from feincms.module.medialibrary.models import MediaFile
from django import forms

from feinheit import translations
from feinheit.location.models import CountryField

class Category(models.Model):
    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), unique=True)
    
    def __unicode__(self):
        return self.name


class EventManager(translations.TranslatedObjectManager):
    def active(self):
        return self.filter(active=True)
    
    def upcoming(self):
        """ returns all upcoming and ongoing events """
        today = date.today()
        if datetime.now().hour < 6:
            today = today-timedelta(days=1)
        
        return self.active().filter(Q(start_date__gte=today) | Q(end_date__gte=today))
    
    def past(self):
        """ returns all past events """
        today = date.today()
        if datetime.now().hour < 6:
            today = today-timedelta(days=1)
        
        return self.active().filter(Q(start_date__lt=today) & Q(end_date__lt=today))


class Event(models.Model, translations.TranslatedObjectMixin):
    """
    Stores an event entry. An event needs to have at least a start date. There are 3 possible types of events:
        * One day events (only start date is given)
        * Multi day events (start and end date is given)
        * Timed event (start date and time and end date and time are given)
    
    Title, slug and description are translateable trough :model:`feinheit.agenda.EventTranslation`
    """
    
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
            
    active = models.BooleanField(_('Active'))
    
    start_date = models.DateField(_('Start date'))
    start_time = models.TimeField(_('Start time'), blank=True, null=True, help_text=_('leave blank for full day event'))
    end_date = models.DateField(_('End date'), blank=True, null=True, help_text=_('leave blank for one day event'))
    end_time = models.TimeField(_('End time'), blank=True, null=True, help_text=_('leave blank for full day events'))
    
    type = models.CharField(_('Type'), max_length=10, help_text=_('Cachefield for the computed type'), editable=False,
                             choices=(('oneday' ,_('One day event')),
                                      ('multiday',_('Multi day event')),
                                      ('timed',_('Timed event')),
                             ))
    
    image = models.ForeignKey(MediaFile, blank=True, null=True)
    
    address = models.CharField(_('Address'), max_length=150, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    
    categories = models.ManyToManyField(Category, blank=True, null=True)

    objects = EventManager()
    
    @property
    def datetime(self):
        """ datetime property for legacy support """
        return self.start_date
    
    class Meta:
        ordering = ['start_date']
        verbose_name = _('event')
        verbose_name_plural = _('events')
    
    def clean(self):
        """ tries to find the type of the event and stores it in the type field. 
            in this process, it guesses possible forgotten values
        """
        if self.start_time and self.end_date and not self.end_time:
            self.end_time = time(23, 59, 59)
        if self.end_time and not self.start_time:
            self.start_time = time(0)
        if self.start_time and self.end_time and not self.end_date:
            if self.end_time > self.start_time:
                self.end_date = self.start_date
            else:
                self.end_date = self.start_date + timedelta(days=1)
        
        if not self.start_time and not self.end_date and not self.end_time:
            self.end_date = self.start_date
            self.type = 'oneday'
        elif (self.start_date == self.end_date) and not (self.start_time or self.end_time):
            self.type = 'oneday'
        elif self.start_time:
            self.type = 'timed'
        elif self.end_date and not self.start_time:
            self.type = 'multiday'
        
        #an event cant end before start
        if self.end_date < self.start_date:
            raise ValidationError(_('The Event cannot end before start (Start date <= End date)'))
        if (self.end_date == self.start_date) and (self.end_time < self.start_time):
            raise ValidationError(_('The Event cannot end before start (Start time <= End time)'))
    
    @models.permalink
    def get_absolute_url(self):
        #TODO: Make this work
        return ('feinheit.agenda.urls/event_detail', (), {'slug': self.translation.slug})


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


class EventsContent(models.Model):
    filter = models.CharField(max_length=1, choices=(
                                ('a',_('all')),
                                ('u',_('upcoming')),
                                ('p',_('past')),
                            ))
    
    class Meta:
        abstract = True
        verbose_name = _('event list')
        verbose_name_plural = _('event lists')
        
    @property
    def media(self):
        media = forms.Media()
        media.add_js(('/media/sys/feinheit/js/jquery.scrollTo-min.js',
                      'lib/fancybox/jquery.fancybox-1.3.1.pack.js'))
        media.add_css({'all': ('lib/fancybox/jquery.fancybox-1.3.1.css', )})
        
        return media

    def render(self, request, context, **kwargs):
        now = datetime.now()
        today = date.today()
        
        if now.hour < 6: # Still shows tonights events.
            today = date.today()-timedelta(days=1)
            
        if self.filter == 'u':
            object_list = Event.objects.upcoming()
        elif self.filter == 'p':
            object_list = Event.objects.past()
        else:
            object_list = Event.objects.active()
            
        current_page = request.GET.get('page', 1)  
        page = Paginator(object_list, 20).page(current_page)
        
        return render_to_string('content/agenda/event_list.html', 
                {'object_list': object_list, 'page': page, },
                context_instance=RequestContext(request))