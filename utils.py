from faker import Faker
import pyshorteners
import smtplib
from email.mime.text import MIMEText
from db import save_fake_data_to_db

# --- CONFIGURATION (UPDATE THESE WITH YOUR REAL CREDENTIALS) ---
EMAIL_SENDER = "your_real_email@gmail.com"
EMAIL_PASSWORD = "your_16_digit_app_password" # Must be a Gmail App Password, not your regular password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

TWILIO_SID = "ACxxxxxxxxxxxxxxxxxxxx" # Your actual Twilio Account SID
TWILIO_TOKEN = "your_auth_token"      # Your actual Twilio Auth Token
TWILIO_PHONE = "+1234567890"          # Your actual Twilio phone number

fake = Faker()

def generate_and_store_fake_data():
    records = []
    for _ in range(10):
        data = (
            fake.name(),
            fake.address().replace('\n', ', '),
            fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
            fake.phone_number(),
            fake.email(),
            fake.job(),
            fake.company(),
            fake.credit_card_number(),
            fake.url(),
            fake.user_name()
        )
        records.append(data)
    save_fake_data_to_db(records)

def shorten_url(long_url):
    try:
        s = pyshorteners.Shortener()
        return s.tinyurl.short(long_url)
    except Exception as e:
        return f"Error: {str(e)}"

def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Email Error: {str(e)}"

def send_sms(to_number, message):
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=message, from_=TWILIO_PHONE, to=to_number)
        return "SMS sent successfully!"
    except Exception as e:
        return f"SMS Error: {str(e)}"