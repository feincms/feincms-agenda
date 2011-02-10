from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _

from feinheit import translations
from feincms.views.generic.list_detail import object_list
from django.core.paginator import Paginator
from django.template.loader import render_to_string



class Event(models.Model, translations.TranslatedObjectMixin):
    date = models.DateField(_('date'), default=date.today)
    time = models.CharField(_('time'), max_length=50, blank=True)
    image = models.ImageField(_('image'), upload_to='event_images',
        blank=True, null=True)

    class Meta:
        ordering = ['-date']
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

    @models.permalink
    def get_absolute_url(self):
        return ('feinheit.agenda.urls/agenda_event_detail', (), {'slug': self.slug})

class EventsContent(models.Model):

    which = models.CharField(max_length=1, choices=(('u',_('upcoming')),('p',_('past')),))

    class Meta:
        abstract = True
        verbose_name = _('event list')
        verbose_name_plural = _('event lists')

    def render(self, request):
        if self.which == 'u':
            object_list = Event.objects.filter(date__gte=date.today)
        else:
            object_list = Event.objects.filter(date__lte=date.today)
        current_page = request.GET.get('page', 1)  
        page = Paginator(object_list, 20).page(current_page)
        return render_to_string('agenda/event_list.html', locals())
