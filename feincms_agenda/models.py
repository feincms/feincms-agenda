from datetime import date, datetime, timedelta, time

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import ugettext_lazy as _

try:
    import feincms_cleanse as cleanse
except ImportError:  # Use deprecated location
    from feincms.utils.html import cleanse

from feincms.content.application.models import app_reverse
from feincms.module.medialibrary.fields import MediaFileForeignKey
from feincms.module.medialibrary.models import MediaFile
from feincms.module.page.models import Page
from feincms import translations

from .fields import CountryField


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

        return self.active().filter(
            Q(start_date__gte=today) | Q(end_date__gte=today))

    def past(self):
        """ returns all past events """
        today = date.today()
        if datetime.now().hour < 6:
            today = today-timedelta(days=1)

        return self.active().filter(
            Q(start_date__lt=today) & Q(end_date__lt=today))


class Event(models.Model, translations.TranslatedObjectMixin):
    """
    Stores an event entry. An event needs to have at least a start date. There
    are 3 possible types of events:

    * One day events (only start date is given)
    * Multi day events (start and end date is given)
    * Timed event (start date and time and end date and time are given)

    Title, slug and description are translateable trough
    :model:`feincms_agenda.models.EventTranslation`
    """

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.cleanse = getattr(settings, 'EVENT_CLEANSE', False)
        cm = getattr(settings, 'CLEANSE_MODULE', None)
        if cm:
            try:
                # TODO importlib or something else; or reuse the
                # richtext field from FeinCMS and add cleansing there
                self.cleanse_module = __import__(cm, fromlist=True)
            except (ValueError, ImportError):
                raise ImproperlyConfigured(
                    'There was an error importing your %s cleanse_module!' % (
                        self.__name__,))
        else:
            self.cleanse_module = cleanse

    active = models.BooleanField(_('Active'))

    start_date = models.DateField(_('Start date'))
    start_time = models.TimeField(
        _('Start time'), blank=True, null=True,
        help_text=_('leave blank for full day event'))
    end_date = models.DateField(
        _('End date'), blank=True, null=True,
        help_text=_('leave blank for one day event'))
    end_time = models.TimeField(
        _('End time'), blank=True, null=True,
        help_text=_('leave blank for full day events'))

    type = models.CharField(
        _('Type'), max_length=10,
        help_text=_('Cachefield for the computed type'),
        editable=False,
        choices=(
            ('oneday', _('One day event')),
            ('multiday', _('Multi day event')),
            ('timed', _('Timed event')),
            ('timedm', _('Timed event multiple days')),
        ))

    image = MediaFileForeignKey(MediaFile, blank=True, null=True)

    feincms_page = models.ForeignKey(
        Page, blank=True, null=True,
        help_text=_('FeinCMS Page with additional infos'))

    address = models.CharField(
        _('Address'), max_length=150, blank=True, null=True)
    country = CountryField(blank=True, null=True)

    categories = models.ManyToManyField(
        Category, blank=True, null=True,
        verbose_name=_('categories'))

    objects = EventManager()

    class Meta:
        ordering = ['start_date']
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def get_absolute_url(self):
        return app_reverse(
            'agenda_event_detail', 'feincms_agenda.urls',
            args=(), kwargs={'slug': self.translation.slug})

    @property
    def datetime(self):
        """ datetime property for legacy support """
        return self.start_date

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
        elif (self.start_date == self.end_date) and not (
                self.start_time or self.end_time):
            self.type = 'oneday'
        elif self.start_time:
            if self.start_date == self.end_date:
                self.type = 'timed'
            else:
                self.type = 'timedm'
        elif self.end_date and not self.start_time:
            self.type = 'multiday'

        # an event can't end before it starts
        if self.end_date < self.start_date:
            raise ValidationError(_(
                'The Event cannot end before start (Start date <= End date)'))
        if (self.end_date == self.start_date) and (
                self.end_time < self.start_time):
            raise ValidationError(_(
                'The Event cannot end before start (Start time <= End time)'))


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
            self.description = self.parent.cleanse_module.cleanse_html(
                self.description)
        super(EventTranslation, self).save(*args, **kwargs)
