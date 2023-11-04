from ppl_joinus.models import JoinusEvent, JoinusUserFormBuilder, JoinusRegistration, JoinusFormPage
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup, DeleteView
from django.utils.html import format_html
import json, csv
from django.http import HttpResponse
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.admin.filters import WagtailFilterSet
from wagtail import hooks
from wagtail.snippets.bulk_actions.snippet_bulk_action import SnippetBulkAction
from wagtail.admin.menu import MenuItem
from wagtail.admin.views.bulk_action import BulkAction

class JoinusEventAdmin(SnippetViewSet):
    model = JoinusEvent
    menu_label = 'Joinus Event'
    icon = 'date'
    base_url_path = "joinus-event"
    list_display = ('title', 'total_registered', 'spaces_remaining', 'total_spaces', 'waitlist_spots', 'waitlist_remaining')

    panels = [
    FieldPanel('spots_available'),
    FieldPanel('waitlist_spots_available'),
    FieldPanel('registration_form_chooser'),
    FieldPanel('success_email_msg'),
    FieldPanel('waitlist_email_msg'),
    ]

class DeleteUserInfoView(DeleteView):
	#deletes the user info when a regration is also deleted
	def get_success_message(self):
		cancel_user = JoinusUserFormBuilder.objects.get(id=self.object.user_info.id)
		cancel_user.delete()
		msg = 'The following user info has been deleted:  ' + str(cancel_user)
		return msg

class FilterByEvent(WagtailFilterSet):
	class Meta:
		model = JoinusRegistration
		fields = ['event_name']

class JoinusRegistrationAdmin(SnippetViewSet):
	model = JoinusRegistration
	menu_label = 'Registrations' 
	icon = 'doc-full'
	base_url_path = 'reg'
	list_display = ('name','email', 'event_name', 'registration_date' ,'wait_list')
	index_template_name = 'ppl_joinus/joinusregistration/index.html'
	filterset_class = FilterByEvent
	delete_view_class = DeleteUserInfoView
	edit_template_name = 'ppl_joinus/admin_snippet/edit.html'

	edit_handler = TabbedInterface([
        ObjectList([FieldPanel("registration_date", read_only=True), FieldPanel("user_info", read_only=True), FieldPanel("wait_list")], 
        	heading="Registrant"),
    ])

@hooks.register('register_bulk_action')
class ExportCSV(BulkAction):
	display_name = "Export CSV"
	aria_label = "Export CSV"
	action_type = "export_csv"
	template_name = "ppl_joinus/admin_snippet/export_csv.html"
	models = [JoinusRegistration]
	
	@hooks.register("before_bulk_action")
	def hook_function(request, action_type, objects, action_class_instance, **kwargs):
		if action_type == 'export_csv':
			fields = []
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="export_registration_info.csv"'
			writer = csv.writer(response)

			for obj in objects:
				#the user_info labels are extracted from json in a single field
				user_fields = list(obj.user_info.form_data.keys())
				#convert the obj class to dictionary and extract the keys
				obj_dic_keys = vars(obj).keys()
				#convert to a list
				obj_keys_list = list(obj_dic_keys)
			#remove uneeded labels
			obj_keys_list.remove('user_info_id')
			obj_keys_list.remove('_state')

			#clean up names
			static_fields = []
			for okl in obj_keys_list:
				okl_replace = okl.replace("event_name_id", "event_name")
				static_fields.append(okl_replace)

			fields = static_fields + user_fields

			field_labels = []
			for flds in fields:
				field_labels.append(flds.replace("_", " ").title())
			writer.writerow(field_labels)

			user_info_values = []
			static_values = []
			for obj in objects:
				user_info_values.append(obj.user_info.form_data.values())
				if obj.wait_list == True:
					wait_list = 'Yes'
				elif obj.wait_list == False:
					wait_list = 'No'
				static_values.append(list((obj.id, str(obj.event_name), obj.registration_date.strftime("%Y-%m-%d %H:%M"), wait_list)))

			user_values = [list(val) for val in user_info_values]

			#clean up boolean field output
			for user_info in user_values:
				if ['No'] in user_info:
					user_info[user_info.index(['No'])] = 'No'
				if ['Yes'] in user_info:
					user_info[user_info.index(['Yes'])] = 'Yes'

			registration_values = []

			for static, user in zip(static_values, user_values):
				registration_values.append(static + user)

			for rv in registration_values:
				writer.writerow(rv)
			#uncomment to test output without exporting a CSV
			#return HttpResponse(f"{registration_values}", content_type="text/plain")
			return response

class JoinusFormAdmin(SnippetViewSet):
    model = JoinusFormPage
    menu_label = 'Registration Form'
    icon = 'form'
    base_url_path = "joinus-form"

class JoinusEventAdminGroup(SnippetViewSetGroup):
	menu_label = 'Registration'
	menu_icon = 'list-ul'
	items = (JoinusEventAdmin, JoinusRegistrationAdmin, JoinusFormAdmin)

register_snippet(JoinusEventAdminGroup)