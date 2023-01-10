import string
import random
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail as sendmail

class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list, html, fail_silently):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.fail_silently = fail_silently
        self.html = html
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(
            self.subject, self.message, self.from_email, to=self.recipient_list)
        if self.html:
            msg.attach_alternative(self.html, "text/html")
        msg.send(self.fail_silently)


def send_mail(subject, recipient_list, *args, message, from_email=settings.EMAIL_HOST_USER,  html_message=None, fail_silently=False,**kwargs):
    EmailThread(subject, message, from_email, recipient_list, html_message, fail_silently).start()