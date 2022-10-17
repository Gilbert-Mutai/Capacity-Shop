from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import threading

class EmailThread(threading.Thread):

    def __init__(self,email):
        self.email = email

        threading.Thread.__init__(self)
    def run(self):
        self.email.send()


    

def send_welcome_email(name,receiver):
    # Creating message subject and sender
    subject = 'Welcome to Capacity Limited'
    sender = 'fitstargilii1194@gmail.com'

    #passing in the context vairables
    text_content = render_to_string('email/register-email.txt',{"name": name})
    html_content = render_to_string('email/register-email.html',{"name": name})

    email = EmailMultiAlternatives(subject,text_content,sender,[receiver])
    email.attach_alternative(html_content,'text/html')

    EmailThread(email).start()
    
