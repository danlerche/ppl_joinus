# ppl_joinus

A simple registration app designed in wagtail cms (django/python) that allows users to register for an event. The registration by design has a default amount of spaces, and includes the option for a waitlist. The registration forms use wagtails form builder app: this allows the event admin to taylor the forms in any way they choose. Events are associated with registration forms so the event editor doesn't need to create a new for for every event. User info is not associated with django's internal user system. This is by design as we want user info to be ephemeral and purged regularly. Much work still to do including:

Email notifications 

CSV Export

Calendar ics creation 

User form data that's saved as JSON needs to be parsed out in the admin

Calendar integration
