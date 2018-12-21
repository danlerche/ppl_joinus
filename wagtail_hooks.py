from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from .models import JoinusEvent, JoinusRegistration

class EventAdmin(ModelAdmin):
    model = JoinusEvent
    menu_label = 'Events'
    add_to_settings_menu = True
    exclude_from_explorer = False


class RegistrationAdmin(ModelAdmin):
    model = JoinusRegistration
    menu_label = 'Event Registrations'
    list_display = ('event_name', 'user_info', 'wait_list', 'registration_date')
    list_filter = ['event_name']
    add_to_settings_menu = True
    exclude_from_explorer = True

modeladmin_register(EventAdmin)
modeladmin_register(RegistrationAdmin)
