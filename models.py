import json
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, FieldRowPanel, PageChooserPanel
from django import forms
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import AbstractFormField, AbstractForm, AbstractEmailForm, AbstractFormSubmission
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.models import Page
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from wagtail.snippets.views.snippets import DeleteView

RESERVED_LABELS = ['Your Name', 'Email']

def validate_label(value):
    if value in RESERVED_LABELS:
        raise ValidationError("'%s' is reserved." % value)

class JoinusEvent(Page):
    body = RichTextField(blank=True)
    date = models.DateTimeField()
    spots_available = models.PositiveIntegerField(default=0)
    waitlist_spots_available = models.PositiveIntegerField(default=0)
    registration_form_chooser = models.ForeignKey('JoinusFormPage', default=1, blank=False, on_delete=models.SET_NULL, null=True)
    success_email_msg = RichTextField(blank=True, null=True, verbose_name="Body of the success email")
    waitlist_email_msg = models.CharField(max_length=2000, blank=True, null=True, verbose_name="Body of the waitlist email")
    success_page = models.ForeignKey('wagtailcore.Page', blank=False, on_delete=models.SET_NULL, null=True, related_name="registration_success")
    content_panels = AbstractForm.content_panels + [
        FieldPanel('body', classname="full"),
        FieldPanel('date', classname="full"),
        FieldPanel('spots_available', classname="full"),
        FieldPanel('waitlist_spots_available', classname="full"),
        FieldPanel('success_email_msg', classname="full"),
        FieldPanel('waitlist_email_msg', widget=forms.Textarea, classname="full"),
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
                    messages.success(request, 'You have succesfully registered for ' + self.title)
                    url = self.success_page.url
                    
                    submission_email = custom_form.cleaned_data['email']
                    subject = 'You have succesfully registered for ' + self.title
                    plain_message = strip_tags(self.success_email_msg)
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [submission_email]
                    if from_email !='':
                        send_mail(subject, plain_message, from_email, [submission_email], html_message=self.success_email_msg)

                    return redirect(url, permanent=False)

                elif custom_form.is_valid() and current_spots == 0 and current_waitlist_spots > 0:
                    form_submission = registration_form_page.process_form_submission(custom_form)
                    user_instance = get_primary
                    registration = JoinusRegistration(event_name=event_instance, user_info_id=get_primary[0], wait_list=1)
                    registration.save()
                    messages.success(request, 'You have been added to the waitlist for ' + self.title)
                    url = self.success_page.url
                    #email function here

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


    def total_registered(self):
        total_registered = JoinusRegistration.objects.filter(event_name_id=self.page_ptr_id, wait_list=0).count()
        return total_registered

    def total_spaces(self):
        return self.spots_available

    def spaces_remaining(self):
        total_registered = JoinusRegistration.objects.filter(event_name_id=self.page_ptr_id, wait_list=0).count()
        spaces_remaining = self.spots_available - total_registered
        return spaces_remaining

    def waitlist_spots(self):
        return self.waitlist_spots_available

    def waitlist_remaining(self):
        current_waitlisted = JoinusRegistration.objects.filter(event_name_id=self.page_ptr_id, wait_list=1).count()
        waitlist = self.waitlist_spots_available - current_waitlisted
        return waitlist

class JoinusFormField(AbstractFormField):
    form_builder_page = ParentalKey('JoinusFormPage', on_delete=models.CASCADE, related_name='form_fields')
    label = models.CharField(
        verbose_name='label',
        max_length=255,
        help_text='The label of the form field, cannot be one of the following: %s.'
        % ', '.join(RESERVED_LABELS),
        validators=[validate_label]
    )

class JoinusFormPage(AbstractEmailForm):

    content_panels = AbstractForm.content_panels + [
        FormSubmissionsPanel(),
        InlinePanel('form_fields', label="Form fields"),
    ]

    def get_submission_class(self):
        return JoinusUserFormBuilder

    def process_form_submission(self, form):
        create_submission = self.get_submission_class().objects.create(form_data=form.cleaned_data, page=self)
        get_submission = self.get_submission_class().objects.filter(pk=create_submission.id).values('id')
        global get_primary
        get_primary = [id['id'] for id in get_submission]

    def get_form_fields(self):

            fields = list(super(JoinusFormPage, self).get_form_fields())

            fields.insert(0, JoinusFormField(
                label='Email',
                field_type='email',
                required=True,
                help_text="Your email address"))

            fields.insert(0, JoinusFormField(
                label='Your Name',
                field_type='singleline',
                required=False,
                help_text="Your First and Last Name"))

            return fields

    class Meta:
        verbose_name = "Joinus Form Builder"


class JoinusUserFormBuilder(AbstractFormSubmission):
    pass

class JoinusRegistration(models.Model):
    user_info = models.ForeignKey('JoinusUserFormBuilder', default=1, on_delete=models.CASCADE)
    event_name = models.ForeignKey('JoinusEvent', default=1, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True, blank=True)
    wait_list = models.BooleanField(default=0)

    def name(self):
        user_info = self.user_info.form_data
        return user_info.get('your_name', None)

    def email(self):
        email = self.user_info.form_data
        return email.get('email', None)

    def __str__(self):
        return self.event_name.title

    class Meta:
        verbose_name = "Event Registration"