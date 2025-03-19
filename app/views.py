from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, User


def index(request):
    return render(request, "index.html")


def login(request):
    if request.POST:
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.get(email=email, password=password)
        if user:
            # request.session
            user = User.objects.get(email=email)
            return redirect(f"/profile/{user.username}")

    return render(request, "login.html")


def register(request):
    if request.POST:
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if email and username and password:
            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "A user with this username already exists.")
            else:
                user = User(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Registration successful!")
                return redirect("/login")

    return render(request, "register.html")


def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "profile.html", {"user": user})


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
            return redirect(f"/product/{product.id}")
    return render(request, "add.html")


def update(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.POST:
        name = request.POST.get("product-name")
        price = request.POST.get("price")
        desc = request.POST.get("description")

        if name and price:
            product.name = name
            product.price = price
            product.desc = desc
            product.save()
            return redirect(f"/product/{id}")
    return render(request, "update.html", {"product": product})


def delete(request, id):
    product = get_object_or_404(Product, pk=id)
    product.delete()
    return redirect("/market")
