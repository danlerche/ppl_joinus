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
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="export_registration_info.csv"'
			
			writer = csv.writer(response)
			fieldnames = [field.name for field in JoinusRegistration._meta.get_fields()]

			writer.writerow(fieldnames)

			#for obj in JoinusRegistration.objects.all():
			#	writer.writerow([str(getattr(obj, field)) for field in fieldnames])
			for obj in objects:
				writer.writerow([str(getattr(obj, field)) for field in fieldnames])

			return response
			#return HttpResponse(f"{len(objects)} objects would be exported", content_type="text/plain")

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