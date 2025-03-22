from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product, User


def index(request):
    return render(request, "index.html", {"user": request.user})


def about(request):
    return render(request, "about.html", {"user": request.user})


def register(request):
    if request.POST:
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if email and username and password:
            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists")
                return redirect("/register")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "A user with this username already exists")
                return redirect("/register")
            else:
                User.objects.create_user(
                    username=username, email=email, password=password
                )
                messages.success(request, "Registration successful")
                return redirect("/login")

    return render(request, "register.html", {"user": request.user})


def login_user(request):
    if request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect("/profile")
        else:
            messages.error(request, "Username or password is incorrect")
            return redirect("/login")

    return render(request, "login.html", {"user": request.user})


def profile(request, username=None):
    if username:
        try:
            user = User.objects.get(username=username)
            return render(request, "profile.html", {"user": user})
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect("/login")  # should go to 404

    if request.user.is_authenticated:
        return render(request, "profile.html", {"user": request.user})
    return redirect("/login")


def product(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        messages.error(request, "product does not exist")
        return redirect("/market")  # should go to 404

    return render(request, "product.html", {"user": request.user, "product": product})


def add(request):
    if not request.user.is_authenticated:
        return redirect("/market")

    if request.POST:
        name = request.POST.get("product-name")
        price = request.POST.get("price")
        desc = request.POST.get("description")
        if name and price:
            product = Product(name=name, price=price, desc=desc)
            product.save()
            return redirect(f"/product/{product.id}")

    return render(request, "add.html", {"user": request.user})


def update(request, id):
    if not request.user.is_authenticated:
        return redirect(f"/product/{id}")

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

    return render(request, "update.html", {"user": request.user, "product": product})


def delete(request, id):
    if not request.user.is_authenticated:
        return redirect(f"/product/{id}")

    product = get_object_or_404(Product, pk=id)
    product.delete()
    return redirect("/market")


def market(request):
    products = Product.objects.all()
    return render(request, "market.html", {"user": request.user, "products": products})
