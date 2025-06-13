import io

from django.contrib import messages
from django.shortcuts import redirect
import matplotlib.pyplot as plt
import numpy as np
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template

from app import models


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


def sales_plot(request):
    names, qs, ts = [], [], []

    hists = models.History.objects.filter(author=request.user)
    if hists.count() < 1:
        messages.error(request, "you have no sales to plot")
        return redirect("/sales")

    sales = hists.values("name", "total").annotate(quantity=Sum("quantity"))

    for sale in sales:
        names.append(sale["name"])
        qs.append(sale["quantity"])
        ts.append(sale["total"])

    data = {"quantity": qs, "revenue": ts}

    x = np.arange(len(names))

    fig, ax = plt.subplots(layout="constrained")

    width, mult = 0.25, 0
    for q, t in data.items():
        offset = width * mult
        rects = ax.barh(x + offset, t, width, label=q)
        ax.bar_label(rects, padding=3)
        mult += 1

    ax.set_title("Product Sales")
    ax.set_xlabel("quantity sold / revenue")
    ax.set_yticks(x + width, names)
    ax.legend(loc="upper right", ncols=2)
    ax.set_xlim(0, 250)

    buf = io.BytesIO()
    plt.savefig(buf, format="jpg")
    buf.seek(0)
    plt.close(fig)

    response = HttpResponse(buf.getvalue(), content_type="image/jpg")
    response["Content-Disposition"] = 'attachment; filename="sales.jpg"'
    return response
