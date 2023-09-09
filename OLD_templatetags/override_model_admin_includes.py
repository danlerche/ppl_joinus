import datetime
from django.contrib.admin.templatetags.admin_list import ResultList, result_headers
from django.contrib.admin.utils import display_for_field, display_for_value, lookup_field
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms.utils import flatatt
from django.template import Library
from django.template.loader import get_template
from django.utils.encoding import force_str
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from django.template import Library

register = Library()

@register.simple_tag
def admin_list_filter_override(view, spec):
    template_name = spec.template
    if template_name == 'admin/filter.html':
        template_name = 'ppl_joinus/modeladmin/includes/filter.html'
    tpl = get_template(template_name)
    return tpl.render({
        'title': spec.title,
        'choices': list(spec.choices(view)),
        'spec': spec,
    })
