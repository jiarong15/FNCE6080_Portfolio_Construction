from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, From, To, Subject, ReplyTo, Content, MimeType)
import datetime
import string
import random

def generate_otp():
    """Generate a 6-digit OTP using random.choices"""
    digits = string.digits
    otp = ''.join(random.choices(digits, k=6))
    return otp

def send_email_otp(email_recipients_cleaned, recipient_first_name, code):
    html = f"""
    <html><body><p>Hi {recipient_first_name},</p>
    <p>Your OTP Code is as follows:</p>
    <p>{code}</p>
    <p>Regards,<br>Aramco Trading Singapore</p>
    </body></html>
    """

    recipients = [To(email=email_recipients_cleaned)]

    sender="info@atc-apps.com"
    sender_name="ATS Analytics (sent via SendGrid)"
    subject = "Email OTP (Vessels Tracking Login) " + datetime.datetime.now().strftime("%d-%m-%y")

    message = Mail()
    message.from_email = From(sender, sender_name)
    message.to = recipients

    message.subject = Subject(subject)
    message.reply_to = ReplyTo('ats-analytics@aramcotrading.sg')
    message.content = Content(MimeType.html, html)

    SendGrid_API_key = "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" 
    sg = SendGridAPIClient(api_key=SendGrid_API_key)

    try:
        response = sg.send(message)
    except Exception as e:
        print(e)
