from django.shortcuts import render

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
    return render(request, "product.html", { "products": products })
