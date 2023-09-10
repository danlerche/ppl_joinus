from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.contrib.modeladmin.views import IndexView
from .models import JoinusEvent, JoinusUserFormBuilder, JoinusRegistration, JoinusFormPage
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html
from django.http import HttpResponse
from wagtail.core import hooks
import json, itertools, csv
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from wagtail.contrib.modeladmin.views import IndexView
from wagtail.contrib.modeladmin.helpers import AdminURLHelper, ButtonHelper


class EventAdmin(ModelAdmin):
    model = JoinusFormPage
    menu_label = 'Registration Forms'
    add_to_settings_menu = True
    exclude_from_explorer = False


class RegistrationFormsAdmin(ModelAdmin):
    model = JoinusEvent
    menu_label = 'Events'
    add_to_settings_menu = True
    exclude_from_explorer = False

class ExportButtonHelper(ButtonHelper):

    export_all_events_button_classnames = ['icon', 'icon-download']
    export_single_event_button_classnames = ['icon', 'icon-download']

    def export_all_events_button(self, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []

        classnames = self.export_all_events_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        text = _('Export {}'.format(self.verbose_name_plural.title()))

        return {
            'url': self.url_helper.get_action_url('export_all_events', query_params=self.request.GET),
            'label': text,
            'classname': cn,
            'title': text,
        }

    def export_single_event_button(self, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []

        classnames = self.export_single_event_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        text = _('Export {}'.format(self.verbose_name_plural.title()))

        return {
            'url': self.url_helper.get_action_url('export_single_event', query_params=self.request.GET),
            'label': text,
            'classname': cn,
            'title': text,
        }

class ExportAdminURLHelper(AdminURLHelper):
    non_object_specific_actions = ('create', 'choose_parent', 'index', 'export_all_events', 'export_single_event')

    def get_action_url(self, action, *args, **kwargs):
        query_params = kwargs.pop('query_params', None)

        url_name = self.get_action_url_name(action)
        if action in self.non_object_specific_actions:
            url = reverse(url_name)
        else:
            url = reverse(url_name, args=args, kwargs=kwargs)

        if query_params:
            url += '?{params}'.format(params=query_params.urlencode())

        return url

    def get_action_url_pattern(self, action):
        if action in self.non_object_specific_actions:
            return self._get_action_url_pattern(action)

        return self._get_object_specific_action_url_pattern(action)


class ExportAllEventsView(IndexView):

    def export_all_events_csv(self):
        data = self.queryset.all()

        data_headings = [field.verbose_name for field
                         in JoinusRegistration._meta.get_fields()]

        del data_headings[1] #removes the user_info heading as it is replaced by parsed json keys

        # return a CSV instead
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment;filename=' + \
            'all_event_registrations.csv'

        # Prevents UnicodeEncodeError for labels with non-ansi symbols
        data_headings = [smart_str(label) for label in data_headings]

        writer = csv.writer(response)

        user_csv_headings_list = []

        for heading_info in data:
            user_json = str(heading_info.user_info)
            json_loads = json.loads(user_json)
            user_csv_headings_list = list(json_loads.keys())

        first_three_headings =  user_csv_headings_list[0:3]
        writer.writerow(data_headings + first_three_headings)

        for reg in data:
            if reg.wait_list == True:
                reg.wait_list = 'Yes'
            else:
                reg.wait_list = 'No'
            user_csv_values_list = []
            user_json = str(reg.user_info)
            json_loads = json.loads(user_json)
            user_csv_values_list = list(json_loads.values())
            first_three_values = (user_csv_values_list[0:3])
            data_row = []
            data_row.extend([
                reg.id, reg.event_name, reg.registration_date, reg.wait_list
            ])

            writer.writerow(data_row + first_three_values)

        return response

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        return self.export_all_events_csv()

class ExportSingleEventView(IndexView):

    def export_single_event_csv(self):
        data = self.queryset.all()

        data_headings = [field.verbose_name for field
                         in JoinusRegistration._meta.get_fields()]

        del data_headings[1] #removes the user_info heading as it is replaced by parsed json keys

        # return a CSV instead
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment;filename=' + \
            'event_registrations.csv'

        # Prevents UnicodeEncodeError for labels with non-ansi symbols
        data_headings = [smart_str(label) for label in data_headings]

        writer = csv.writer(response)

        user_csv_headings_list = []

        for heading_info in data:
            user_json = str(heading_info.user_info)
            json_loads = json.loads(user_json)
            user_csv_headings_list = list(json_loads.keys())

        writer.writerow(data_headings + user_csv_headings_list)

        for reg in data:
            if reg.wait_list == True:
                reg.wait_list = 'Yes'
            else:
                reg.wait_list = 'No'
            user_csv_values_list = []
            user_json = str(reg.user_info)
            json_loads = json.loads(user_json)
            user_csv_values_list = list(json_loads.values())
            data_row = []
            data_row.extend([
                reg.id, reg.event_name, reg.registration_date, reg.wait_list
            ])

            writer.writerow(data_row + user_csv_values_list)

        return response


    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        return self.export_single_event_csv()

class ExportModelAdminMixin(object):
    """
    A mixin to add to your model admin which hooks the different helpers, the view and register the new urls.
    """

    button_helper_class = ExportButtonHelper
    url_helper_class = ExportAdminURLHelper

    export_all_events_view_class = ExportAllEventsView
    export_single_event_view_class = ExportSingleEventView

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        urls += (
            url(
                self.url_helper.get_action_url_pattern('export_all_events'),
                self.export_all_events_view,
                name=self.url_helper.get_action_url_name('export_all_events')
            ),
            url(
                self.url_helper.get_action_url_pattern('export_single_event'),
                self.export_single_event_view,
                name=self.url_helper.get_action_url_name('export_single_event')
            ),
        )

        return urls

    def export_all_events_view(self, request):
        kwargs = {'model_admin': self}
        view_class = self.export_all_events_view_class
        return view_class.as_view(**kwargs)(request)

    def export_single_event_view(self, request):
        kwargs = {'model_admin': self}
        view_class = self.export_single_event_view_class
        return view_class.as_view(**kwargs)(request)

class RegistrationAdmin(ExportModelAdminMixin, ModelAdmin):
    model = JoinusRegistration
    menu_label = 'Event Registrations' 
    list_display = ('event_name','user_info_parsed', 'registration_date', 'wait_list_rewrite', 'cancelled_rewrite',)

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

    def cancelled_rewrite(self, obj):
                if obj.cancelled == 0:
                    return 'No'
                else: 
                    return 'Yes'
    
    user_info_parsed.short_description = "Registraiton Info"
    wait_list_rewrite.short_description = "Wait listed"
    cancelled_rewrite.short_description = "Cancelled"
    list_filter = ['event_name', 'wait_list', 'cancelled']
    add_to_settings_menu = True
    exclude_from_explorer = True
    index_template_name = 'ppl_joinus/modeladmin/index.html'
    button_helper_class = ExportButtonHelper

modeladmin_register(EventAdmin)
modeladmin_register(RegistrationAdmin)
modeladmin_register(RegistrationFormsAdmin)
