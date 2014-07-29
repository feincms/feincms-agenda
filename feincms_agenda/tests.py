from datetime import date

from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import simplejson

from models import Event


class AgendaTest(TestCase):
    def setUp(self):
        self.event = Event(
            active=True,
            start_date=date(2011, 8, 1),
            address='bahnhofstrasse 1, 8001 zurich')
        self.event.save()
        self.factory = RequestFactory()

    def test_eventpage(self):
        pass

    def test_api(self):
        from api import events

        request = self.factory.get('api/events/')
        response = events(request)
        self.assertEqual(response.status_code, 200)
        python_obj = simplejson.loads(response.content)
        self.assertEqual(python_obj[0]['fields']['start_date'], u'2011-08-01')
