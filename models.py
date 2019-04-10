import json
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel, PageChooserPanel
)
from wagtail.core.fields import RichTextField
from wagtail.contrib.forms.models import AbstractFormField, AbstractForm, AbstractEmailForm, AbstractFormSubmission
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.core.models import Page
from django.shortcuts import render, redirect
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

class SuccessPage(Page):
    body = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

class JoinusEvent(Page):
    body = RichTextField(blank=True)
    date = models.DateTimeField()
    spots_available = models.PositiveIntegerField(default=0)
    waitlist_spots_available = models.PositiveIntegerField(default=0)
    registration_form_chooser = models.ForeignKey('JoinusFormPage', default=1, blank=True, on_delete=models.SET_NULL, null=True)
    success_page = models.ForeignKey('SuccessPage', default=1, blank=True, on_delete=models.SET_NULL, null=True)
    content_panels = AbstractForm.content_panels + [
        FieldPanel('body', classname="full"),
        FieldPanel('date', classname="full"),
        FieldPanel('spots_available', classname="full"),
        FieldPanel('waitlist_spots_available', classname="full"),
        PageChooserPanel('registration_form_chooser'),
        PageChooserPanel('success_page'),
    ]

    def serve(self, request, form_submission=None, *args, **kwargs):
            event_instance = JoinusEvent.objects.get(id=self.page_ptr_id)
            current_registered = JoinusRegistration.objects.filter(event_name_id=self.page_ptr_id, wait_list=0).count()
            current_waitlisted = JoinusRegistration.objects.filter(event_name_id=self.page_ptr_id, wait_list=1).count()
            current_spots = self.spots_available - current_registered
            current_waitlist_spots = self.waitlist_spots_available - current_waitlisted

            #Gets the registration page that relates to the form chooser selected by the user in the event page
            #Gets the custom form that relates to the selected Registration form page
            #custom_form = registration_form_page.get_form(request.POST, request.FILES, page=self, user=request.user)

            if request.method == 'POST' and self.registration_form_chooser is not None:
                registration_form_page = JoinusFormPage.objects.get(pk=self.registration_form_chooser)
                custom_form = registration_form_page.get_form(request.POST, request.FILES, page=self, user=request.user)

                if custom_form.is_valid() and current_spots > 0:
                    form_submission = registration_form_page.process_form_submission(custom_form)
                    user_instance = get_primary
                    registration = JoinusRegistration(event_name=event_instance, user_info_id=get_primary[0], wait_list=0)
                    registration.save()
                    #There is a bug here. When the admin changes the spots available or the waitlist amount after people start registering
                    messages.success(request, 'You have signed up for ' + self.title)
                    url = self.success_page.url
                    return redirect(url, permanent=False)

                elif custom_form.is_valid() and current_spots == 0 and current_waitlist_spots > 0:
                    form_submission = registration_form_page.process_form_submission(custom_form)
                    user_instance = get_primary
                    registration = JoinusRegistration(event_name=event_instance, user_info_id=get_primary[0], wait_list=1)
                    registration.save()
                    messages.success(request, 'You have signed up for the ' + self.title + ' waitlist')
                    url = self.success_page.url
                    return redirect(url, permanent=False)

                else:
                    return render(request, 'ppl_joinus/full.html', {
                        'page': self,
                    })

            elif self.registration_form_chooser is not None:
                registration_form_page = JoinusFormPage.objects.get(pk=self.registration_form_chooser)
                user_form = registration_form_page.get_form(page=self, user=request.user)
            else:
                user_form = ''

            return render(request, 'ppl_joinus/joinus_event.html', {
                'page': self,
                'current_registered': current_registered,
                'current_waitlisted': current_waitlisted,
                'current_spots': current_spots,
                'current_waitlist_spots': current_waitlist_spots,
                'event_instance': event_instance,
                'custom_form': user_form,
    })
    class Meta:
        verbose_name = "Joinus Event"

class JoinusFormField(AbstractFormField):
    form_builder_page = ParentalKey('JoinusFormPage', on_delete=models.CASCADE, related_name='form_fields')


class JoinusFormPage(AbstractEmailForm):

    content_panels = AbstractForm.content_panels + [
        FormSubmissionsPanel(),
        InlinePanel('form_fields', label="Form fields"),
    ]

    def get_submission_class(self):
        return JoinusUserFormBuilder

    def process_form_submission(self, form):
        create_submission = self.get_submission_class().objects.create(form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),page=self)
        get_submission = self.get_submission_class().objects.filter(pk=create_submission.id).values('id')
        global get_primary
        get_primary = [id['id'] for id in get_submission]

    class Meta:
        verbose_name = "Joinus Form Builder"


class JoinusUserFormBuilder(AbstractFormSubmission):
    pass

class JoinusRegistration(models.Model):
    user_info = models.ForeignKey('JoinusUserFormBuilder', default=1, on_delete=models.CASCADE)
    event_name = models.ForeignKey('JoinusEvent', default=1, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True, blank=True)
    wait_list = models.BooleanField(default=0)

    def __str__(self):
        return self.event_name.title

    class Meta:
        verbose_name = "Event Registrations"
