from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Product


def index(request):
    products = Product.objects.all()
    return render(request, "index.html", {"products": products})


def login(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def about(request):
    return render(request, "about.html")


def product(request, id):
    products = Product.objects.get(pk=id)
    return render(request, "product.html", {"products": products})


def add(request):
    if request.POST:
        name = request.POST.get("product-name")
        price = request.POST.get("price")
        desc = request.POST.get("description")
        if name and price:
            product = Product(name=name, price=price, desc=desc)
            product.save()
            return HttpResponseRedirect(f"/product/{product.id}")
    else:
        return render(request, "add.html")
