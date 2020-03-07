from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.contrib.modeladmin.views import IndexView
from .models import JoinusEvent, JoinusUserFormBuilder, JoinusRegistration
import json, itertools, csv
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html
from django.http import HttpResponse
from wagtail.core import hooks

class EventAdmin(ModelAdmin):
    model = JoinusEvent
    menu_label = 'Events'
    add_to_settings_menu = True
    exclude_from_explorer = False

class UserAdmin(ModelAdmin):
    model = JoinusUserFormBuilder
    menu_label = 'Registrants'
    add_to_settings_menu = True
    exclude_from_explorer = False


# Check this out for creating a download CSV option: https://parbhatpuri.com/add-download-csv-option-in-wagtail-modeladmin.html

class showEvents(IndexView):

    def get_events_and_users(events):
      pass


class RegistrationAdmin(ModelAdmin):
    model = JoinusRegistration
    menu_label = 'Event Registrations' 
    list_display = ('event_name','user_info_parsed', 'registration_date', 'wait_list_rewrite',)

    def user_info_parsed(self, obj):
            user_info_str = str(obj.user_info)
            user_info_loads = json.loads(user_info_str)
            user_info_list = list(user_info_loads.values())
            user_label_list = list(user_info_loads.keys())
            format_label_info = ""
            format_user_info = ""
            pair_to_list = []
            format_label_to_list = []
            format_values_to_list = []
            formated_html = ""

            for add_th_tags in user_label_list:
                        format_label_info = format_html('<span class="field-user_label_items col-sm"><strong>{}{}</strong></span>{}', add_th_tags, ': ', '*')
                        format_label_to_list += format_label_info.split('*')
                        del format_label_to_list[-1]

            for add_td_tags in user_info_list:
                        format_user_info = format_html('<span class="field-user_value_items col-sm">{}</span><br/>', add_td_tags)
                        format_values_to_list += format_user_info.split('*')

            for pair_lists_to_tuple in zip (format_label_to_list, format_values_to_list):
                    pair_to_list = list(pair_lists_to_tuple)

                    for i in pair_to_list:
                        formated_html += format_html(i)

            outer_html_beg = '<div class="field-reg-item">'
            outer_html_end = '</div>'
            outer_html = outer_html_beg + formated_html + outer_html_end
            return format_html(outer_html)

    def wait_list_rewrite(self, obj):
                if obj.wait_list == 0:
                    return 'No'
                else: 
                    return 'Yes'

    @hooks.register("insert_global_admin_js", order=100)
    def global_admin_js():
        """Add custom.js to the admin."""
        return format_html(
            '<script src="{}"></script>',
            static("/js/user_info_parsed.js")
        )
    
    user_info_parsed.short_description = "Registraiton Info"
    wait_list_rewrite.short_description = "Wait listed"
    list_filter = ['event_name']
    add_to_settings_menu = True
    exclude_from_explorer = True
    index_template_name = 'ppl_joinus/modeladmin/index.html'
    #index_view_class = showEvents


modeladmin_register(EventAdmin)
modeladmin_register(UserAdmin)
modeladmin_register(RegistrationAdmin)