import os

from django.http import HttpResponse

import sendgrid
from sendgrid.helpers.mail import *


def index(request):
    sg = sendgrid.SendGridAPIClient(
        apikey=os.environ.get('SENDGRID_API_KEY')
    )
    from_email = Email('danielpicone2@gmail.com')
    to_email = Email('danielpicone2@gmail.com')
    subject = 'Sending with SendGrid is Fun'
    content = Content(
        'text/plain',
        'and easy to do anywhere, even with Python'
    )
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())

    return HttpResponse('Email Sent!')
