from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from feincms.module.medialibrary.thumbnail import admin_thumbnail
from feincms.translations import admin_translationinline

from .models import Event, EventTranslation, Category


class EventAdminForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))

    class Meta:
        model = Event


class EventTranslationForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'vLargeTextField tinymce'}),
        required=False)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    save_on_top = True
    list_display = (
        '__unicode__', 'start_date', 'start_time',
        'end_date', 'end_time', 'type', 'active', 'address',
        'country', 'admin_thumbnail')
    fieldsets = [
        (None, {
            'fields': (
                'active',
                ('start_date', 'start_time'),
                ('end_date', 'end_time'),
                ('image', 'feincms_page'),
                ('address', 'country'),
                'categories')
        }),
    ]
    list_filter = ('start_date', 'active')
    raw_id_fields = ('feincms_page', 'image')
    inlines = [
        admin_translationinline(
            EventTranslation,
            prepopulated_fields={'slug': ('title',)},
            form=EventTranslationForm),
        ]

    def admin_thumbnail(self, instance):
        if not instance.image:
            return u''
        image = admin_thumbnail(instance.image)
        if image:
            return mark_safe(
                u"""
                <a href="%(url)s" target="_blank">
                    <img src="%(image)s" alt="" />
                </a>""" % {
                    'url': instance.image.url,
                    'image': image,
                })

        return u''
    admin_thumbnail.short_description = _('Image')
    admin_thumbnail.allow_tags = True


admin.site.register(Category, CategoryAdmin)
admin.site.register(Event, EventAdmin)
