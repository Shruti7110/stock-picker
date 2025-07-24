import resend
import os

# send_test_email()
def send_test_email(subject: str, text_body: str):
    # Set your Resend API key
    resend.api_key = os.environ.get("RESEND_API_KEY")

    # Compose and send email
    response = resend.Emails.send({
        "from": "shruti.pawar@varnyaa.com",  # Must be a verified sender in Resend
        "to": ["shruti.all.1111@gmail.com"],  # Recipient list
        "subject": f"{subject}",
        "text": f"{text_body}"
    })

    print("Email is sent. id: {response.id}")

# send_test_email("hello", "test")