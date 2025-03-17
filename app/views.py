from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from .models import Product


def index(request):
    return render(request, "index.html")


def login(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def about(request):
    return render(request, "about.html")


def market(request):
    products = Product.objects.all()
    return render(request, "market.html", {"products": products})


def product(request, id):
    product = Product.objects.get(pk=id)
    return render(request, "product.html", {"product": product})


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


def delete(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Exception as e:
        raise Http404("Product does not exist\nerror: ", e)
    product.delete()
    return HttpResponseRedirect("/market")
