from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def urlize_target_blank(value, autoescape=True):
    """
    Converts URLs in text into clickable links opening in a new window.
    """
    if not value:
        return ""
    
    # Regex to find URLs
    url_regex = re.compile(r'(https?://[^\s]+)')
    
    def replace(match):
        url = match.group(0)
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer" class="text-prime-orange hover:underline break-all">{url}</a>'
    
    return mark_safe(url_regex.sub(replace, value))

@register.filter
def get_item(dictionary, key):
    """
    Dictionary lookup filter. Usage: {{ my_dict|get_item:my_key }}
    """
    return dictionary.get(key)