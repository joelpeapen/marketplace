from django.shortcuts import render

from .models import *


def index(request):
    return render(request, "index.html")


def login(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def about(request):
    return render(request, "about.html")


def product(request):
    # get product info from database
    products = None
    return render(request, "product.html", {"products": products})


def product_add(request):
    if request.POST:
        name = request.POST["product-name"]
        price = request.POST["price"]
        desc = request.POST["description"]
        obj = Product.objects.create(name=name, price=price, desc=desc)
        # return render(request, "product.html", {"name": name, "price": price, "desc": desc})
    else:
        return render(request, "product_add.html")
