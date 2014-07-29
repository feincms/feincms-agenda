from datetime import datetime

from django import forms
from django.core.paginator import Paginator
from django.db import models
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from .models import Event


class EventsContent(models.Model):
    filter = models.CharField(
        max_length=1,
        choices=(
            ('a', _('all')),
            ('u', _('upcoming')),
            ('p', _('past')),
        ))

    class Meta:
        abstract = True
        verbose_name = _('event list')
        verbose_name_plural = _('event lists')

    @property
    def media(self):
        media = forms.Media()
        # TODO really? Fix paths
        media.add_js((
            '/media/sys/feinheit/js/jquery.scrollTo-min.js',
            'lib/fancybox/jquery.fancybox-1.3.1.pack.js'))
        media.add_css({
            'all': ('lib/fancybox/jquery.fancybox-1.3.1.css', )})

        return media

    def render(self, request, context, **kwargs):
        if self.filter == 'u':
            object_list = Event.objects.upcoming()
        elif self.filter == 'p':
            object_list = Event.objects.past()
        else:
            object_list = Event.objects.active()

        # TODO InvalidPage exceptions etc.
        current_page = request.GET.get('page', 1)
        page = Paginator(object_list, 20).page(current_page)

        return render_to_string('content/agenda/event_list.html', {
            'object_list': object_list,
            'page': page,
        }, context_instance=context)


class EventMapContent(models.Model):
    filter = models.CharField(
        max_length=1,
        choices=(
            ('a', _('all')),
            ('u', _('upcoming')),
            ('p', _('past')),
        ))

    class Meta:
        abstract = True
        verbose_name = _('event map')
        verbose_name = _('event maps')

    @property
    def media(self):
        media = forms.Media()
        media.add_js((
            'http://maps.google.com/maps/api/js?sensor=false',
            '/media/js/event_map.js'))
        media.add_css({
            'all': ('/media/css/event_map.css', )})
        return media

    def render(self, request, context, **kwargs):
        return render_to_string(
            'content/agenda/event_map.html',
            context_instance=context)


class EventDateFilterContent(models.Model):
    class Meta:
        abstract = True
        verbose_name = _('Event date filter content')
        verbose_name_plural = _('Event date filter contents')

    def render(self, **kwargs):
        dates_dict = SortedDict()
        dates = Event.objects.active().dates('start_date', 'day', order="DESC")

        for date in dates:
            # TODO unstupidify this code using setdefault etc.
            if date.year not in dates_dict:
                dates_dict[date.year] = SortedDict([
                    ('date', datetime(date.year, 1, 1)),
                    ('months', SortedDict()),
                ])

            if date.month not in dates_dict[date.year]['months']:
                dates_dict[date.year]['months'][date.month] = SortedDict([
                    ('date', datetime(date.year, date.month, 1)),
                    ('days', SortedDict()),
                ])

            if date.day not in dates_dict[date.year]['months'][date.month]['days']:  # noqa
                dates_dict[date.year]['months'][date.month]['days'][date.day] = SortedDict([  # noqa
                    ('date', datetime(date.year, date.month, date.day)),
                ])

        return render_to_string('content/agenda/date_filter.html', {
            'content': self,
            'dates_dict': dates_dict,
        }, context_instance=kwargs.get('context'))
