from django.core.mail import send_mail
from django.template.loader import get_template


# TODO: send token with mail
def send_confirmation_email(email, token_id, user_id):
    data = {"token_id": str(token_id), "user_id": str(user_id)}
    message = get_template("email_confirm.txt").render(data)
    send_mail(
        subject="Please confirm your email",
        message=message,
        from_email="admin@app.com",
        recipient_list=[email],
        fail_silently=True,
    )
