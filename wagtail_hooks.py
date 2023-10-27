from ppl_joinus.models import JoinusEvent, JoinusUserFormBuilder, JoinusRegistration, JoinusFormPage
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup, DeleteView
from django.utils.html import format_html
import json
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.admin.filters import WagtailFilterSet

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
	list_display = ('name', 'event_name', 'registration_date' ,'wait_list')
	index_template_name = 'ppl_joinus/joinusregistration/index.html'
	filterset_class = FilterByEvent
	delete_view_class = DeleteUserInfoView
	edit_template_name = 'ppl_joinus/admin_snippet/edit.html'

	edit_handler = TabbedInterface([
        ObjectList([FieldPanel("registration_date", read_only=True), FieldPanel("user_info", read_only=True), FieldPanel("wait_list")], 
        	heading="Registrant"),
    ])

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