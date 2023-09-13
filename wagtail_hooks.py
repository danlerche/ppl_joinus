from ppl_joinus.models import JoinusEvent, JoinusUserFormBuilder, JoinusRegistration, JoinusFormPage
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup, DeleteView
from django.utils.html import format_html
import json
from wagtail.admin.panels import FieldPanel

class JoinusEventAdmin(SnippetViewSet):
    model = JoinusEvent
    menu_label = 'Joinus Event'
    icon = 'date'
    base_url_path = "joinus-event"
    list_display = ('title', 'total_registered', 'spaces_remaining', 'total_spaces', 'waitlist', 'waitlist_remaining')

class JoinusFormAdmin(SnippetViewSet):
    model = JoinusFormPage
    menu_label = 'Registration Form'
    icon = 'form'
    base_url_path = "joinus-form"

#https://stackoverflow.com/questions/69012491/override-wagtail-delete-confirmation-message
class MemberDeleteView(DeleteView):
    def confirmation_message(self):
    	#delete_user = JoinusUserFormBuilder.objects.get(id=self.user_info)
    	return 'deleted'

class JoinusRegistrationAdmin(SnippetViewSet):
	model = JoinusRegistration
	menu_label = 'Registrations' 
	icon = 'doc-full'
	base_url_path = 'reg'
	list_display = ('name', 'event_name', 'registration_date', 'wait_list', 'cancelled',)
	index_template_name = 'ppl_joinus/joinusregistration/index.html'
	delete_view_class = MemberDeleteView
	
	#	user_info_list = list(user_info_loads.values())
	#	user_label_list = list(user_info_loads.keys())
	#	format_label_info = ""
	#	format_user_info = ""
	#	pair_to_list = []
	#	format_label_to_list = []
	#	format_values_to_list = []
	#	formated_html = ""

	#	for add_th_tags in user_label_list:
	#		format_label_info = format_html('<span class="field-user_label_items col-sm"><strong>{}{}</strong></span>{}', add_th_tags, ': ', '*')
	#		format_label_to_list += format_label_info.split('*')
	#		del format_label_to_list[-1]
#
#		for add_td_tags in user_info_list:
#			format_user_info = format_html('<span class="field-user_value_items col-sm">{}</span><br/>', add_td_tags)
#			format_values_to_list += format_user_info.split('*')
#
#		for pair_lists_to_tuple in zip (format_label_to_list, format_values_to_list):
#			pair_to_list = list(pair_lists_to_tuple)
#			for i in pair_to_list:
#				formated_html += format_html(i)
#
#			outer_html_beg = '<div class="field-reg-item">'
#			outer_html_end = '</div>'
#			outer_html = outer_html_beg + formated_html + outer_html_end
#			return format_html(outer_html)

class JoinusEventAdminGroup(SnippetViewSetGroup):
	menu_label = 'Registration'
	menu_icon = 'list-ul'
	menu_order = 200
	items = (JoinusEventAdmin, JoinusFormAdmin, JoinusRegistrationAdmin)

register_snippet(JoinusEventAdminGroup)