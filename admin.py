from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from feinheit import translations
from feinheit.agenda.models import Event, EventTranslation
from feincms.templatetags import feincms_thumbnail
from django.utils.safestring import mark_safe
from feincms.module.medialibrary.models import MediaFile
from feincms.content.medialibrary.models import MediaFileWidget

def admin_thumbnail(obj):
    if obj.image.type == 'image':
        image = None
        try:
            image = feincms_thumbnail.thumbnail(obj.image.file.name, '100x60')
        except:
            pass

        if image:
            return mark_safe(u"""
                <a href="%(url)s" target="_blank">
                    <img src="%(image)s" alt="" />
                </a>""" % {
                    'url': obj.image.file.url,
                    'image': image,})
    return ''
admin_thumbnail.short_description = _('Image')
admin_thumbnail.allow_tags = True


class MediaFileAdminForm(forms.ModelForm):
    image = forms.ModelChoiceField(queryset=MediaFile.objects.filter(type='image'),
                                widget=MediaFileWidget, label=_('media file'))
    class Meta:
        model = Event

class EventTranslationForm(forms.ModelForm):
    
    description = forms.CharField(widget=forms.Textarea(
         attrs={'class':'vLargeTextField tinymce'}), required=False)


class EventAdmin(admin.ModelAdmin):
    model = Event
    form = MediaFileAdminForm
    list_display=('__unicode__', 'datetime', admin_thumbnail )
    inlines=[translations.admin_translationinline(EventTranslation,
        prepopulated_fields={'slug': ('title',)}, form=EventTranslationForm)]
admin.site.register(Event, EventAdmin)
