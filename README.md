# ppl_joinus

A simple registration app designed in wagtail cms (django/python) that allows users to register for an event. The registration by design has a default amount of spaces, and includes the option for a waitlist. The registration forms use wagtails form builder app, so the event admin can taylor the forms in any way they choose. Events are associated with registration forms so the event editor doesn't need to create a new for for every event. Users info is not associated with django's internal user system. This is by design as we want user info to be epheral and prunged regularly.  
