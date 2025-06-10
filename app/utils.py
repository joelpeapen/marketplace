from django.core.mail import send_mail
from django.template.loader import get_template


def send_confirmation_email(email, token_id, change=None):
    data = {"token_id": str(token_id)}
    if change:
        data["email"] = email
        message = get_template("email_change.txt").render(data)
    else:
        message = get_template("email_confirm.txt").render(data)
    send_mail(
        subject="Please confirm your email",
        message=message,
        from_email="admin@app.com",
        recipient_list=[email],
        fail_silently=True,
    )


def send_purchase_email(email, products):
    data = {"products": products}
    message = get_template("purchase.txt").render(data)
    send_mail(
        subject="OpenTrader: You Purchased a Product",
        message=message,
        from_email="admin@app.com",
        recipient_list=[email],
        fail_silently=True,
    )


def send_purchase_email_seller(email, product):
    data = {"product": product}
    message = get_template("sold.txt").render(data)
    send_mail(
        subject="OpenTrader: Products sold",
        message=message,
        from_email="admin@app.com",
        recipient_list=[email],
        fail_silently=True,
    )


def send_review_email(email, product, reviewer, rating, review):
    data = {
        "product": product,
        "reviewer": reviewer,
        "rating": rating,
        "review": review,
    }
    message = get_template("review.txt").render(data)
    send_mail(
        subject="OpenTrader: Review on product",
        message=message,
        from_email="admin@app.com",
        recipient_list=[email],
        fail_silently=True,
    )


def send_username_email(email, username):
    message = get_template("username.txt").render({"username": username})
    send_mail(
        subject="Your OpenTrader username",
        message=message,
        from_email="admin@app.com",
        recipient_list=[email],
        fail_silently=True,
    )


def send_password_email(email, token_id):
    data = {
        "token_id": str(token_id),
        "email": email,
    }
    message = get_template("password.txt").render(data)
    send_mail(
        subject="Your OpenTrader password recovery",
        message=message,
        from_email="admin@app.com",
        recipient_list=[email],
        fail_silently=True,
    )
