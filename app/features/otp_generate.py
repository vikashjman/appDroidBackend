import smtplib
import ssl
from email.message import EmailMessage
# Email configuration
email_sender = 'teamhelpdroid@gmail.com'  # Your email address
email_password = 'ayeadmrgdjpkxhod'  # Your email password



# Generate OTP (you can use your OTP generation code)
def generate_otp():
    import random
    return str(random.randint(1000, 9999))

def send_mail(email_receiver,message,sub="Your OTP for HelpDroid"):
    # Set the subject and body of the 
    if(not email_receiver):
        return
    subject = sub
    body = message

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Create an SMTP connection
    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        print(email_receiver)

    print(f'OTP sent to {email_receiver}')

    


