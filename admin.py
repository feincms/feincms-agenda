from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from feincms.content.medialibrary.models import MediaFileWidget
from feincms.module.medialibrary.models import MediaFile
from feincms.templatetags import feincms_thumbnail

from feinheit import translations

from models import Event, EventTranslation, Category

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
                                widget=MediaFileWidget, label=_('media file'), required=False)
    class Meta:
        model = Event

class EventTranslationForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(
         attrs={'class':'vLargeTextField tinymce'}), required=False)


class CategoryAdmin(admin.ModelAdmin):
    list_display=('name', 'slug')
    prepopulated_fields = {'slug' : ('name',)}
admin.site.register(Category, CategoryAdmin)

class EventAdmin(admin.ModelAdmin):
    form = MediaFileAdminForm
    save_on_top = True
    list_display=('__unicode__', 'start_date', 'start_time', 'end_date', 'end_time', 'type', 'active', 'address', 'country', admin_thumbnail )
    fieldsets = [
        (None, {
            'fields': ('active', ('start_date', 'start_time'), ('end_date', 'end_time'), 'image', ('address', 'country'), 'categories')
        }),
    ]
    list_filter = ('start_date', 'active')
    inlines=[translations.admin_translationinline(EventTranslation,
        prepopulated_fields={'slug': ('title',)}, form=EventTranslationForm)]
admin.site.register(Event, EventAdmin)
