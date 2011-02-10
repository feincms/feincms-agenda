from django.conf import settings

import django

AGENDA_USE_CONTENT_TYPE = getattr(settings, 'AGENDA_USE_CONTENT_TYPE', False)