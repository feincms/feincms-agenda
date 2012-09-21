"""
======
Agenda
======

Reworked agenda module by ssc@feinheit.ch. original agenda by sb@feinheit.ch

The agenda can manage events with categories and types. categories are simply
foreign keys to the category table. types are auto computed. there are 3 types:

#. 'oneday': an event, that starts and ends on the same day, without a time specified.
#. 'multiday': an event, that starts on an other day than it ends, but without start and end times specified.
#. 'timed': an event, with start and end times specified on the same date.
#. 'timedm': an event, with start and end times specified on different dates.

The model tries to find the type according to the data entered.


Usage
=====

- add :mod:`feincms_agenda` to your :setting:`INSTALLED_APPS`
- you can either use the :class:`feincms_agenda.models.EventsContent` or
  add :mod:`feincms_agenda.urls` as FeinCMS Application

**hint:** use the application, if you want to have a detail page with own url
for every event.  if you just want to display a simple eventlist, use the
content.
"""

VERSION = (0, 0, 1, 'pre')
__version__ = '.'.join(map(str, VERSION))
