from django.template.defaultfilters import register
from django.urls import reverse
from django.urls import translate_url as django_translate_url
from django.utils.translation import override as lang_override


@register.simple_tag(takes_context=True)
def change_lang(context, lang):
    path = context['request'].path
    return django_translate_url(path, lang)


@register.simple_tag(takes_context=False)
def translate_url(lang_code, name, *args, **kwargs):
    with lang_override(lang_code):
        return reverse(name, args=args, kwargs=kwargs)
