from django import forms
from django.contrib import admin

from feinheit import translations
from feinheit.agenda import models

class EventTranslationForm(forms.ModelForm):
    
    description = forms.CharField(widget=forms.Textarea(
         attrs={'class':'vLargeTextField tinymce'}), required=False)
    """
    JS inclusion moved to admin template due to consolidation.
    class Media:
        js = ('/media/sys/feinheit/tinymce/tiny_mce.js',
            '/media/js/admin/richtext.js',
        )
    """
admin.site.register(models.Event,
    list_display=('__unicode__', 'date', 'time'),
    inlines=[translations.admin_translationinline(models.EventTranslation,
        prepopulated_fields={'slug': ('title',)}, form=EventTranslationForm
        )],
    )
