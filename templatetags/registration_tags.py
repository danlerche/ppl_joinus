from django import template
from django.shortcuts import render
from ppl_joinus.models import JoinusRegistration

register = template.Library()

@register.inclusion_tag('ppl_joinus/joinusregistration/submission_parse.html', takes_context=True)

def show_registrations(context, filter_by):
	all_registrations = JoinusRegistration.objects.all()
	user_info = JoinusRegistration.objects.user_info.form_data
	
	return {
        'request': context['request'],
        'all_registrations': all_registrations,
        }
