from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

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
                return redirect(request.path)
            elif User.objects.filter(username=username).exists():
                messages.error(request, "A user with this username already exists")
                return redirect(request.path)
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
            return redirect("/user")
        else:
            messages.error(request, "Username or password is incorrect")
            return redirect(request.path)

    return render(request, "login.html", {"user": request.user})


def logout_user(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    logout(request)
    return redirect("/market")


def settings(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    if request.POST:
        email = request.POST.get("email")
        username = request.POST.get("username")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")

        user = request.user
        if username and username != user.username:
            user.username = username

        if email and email != user.email:
            user.email = email

        if fname != user.first_name:
            user.first_name = fname

        if lname != user.last_name:
            user.last_name = lname

        user.save()
        messages.success(request, "Profile Updated")
        return redirect(request.path)

    return render(request, "settings.html", {"user": request.user})


def settings_account(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    if request.POST:
        password = request.POST.get("password")
        old_password = request.POST.get("old-password")
        confirm = request.POST.get("confirm-pw")

        user = request.user

        if not old_password:
            messages.error(request, "Must provide old password to change password")
        elif not password:
            messages.error(request, "Must provide a new password")
        elif not confirm:
            messages.error(request, "Must confirm the new password")
        elif password != confirm:
            messages.error(request, "Passwords do not match")
        elif not user.check_password(old_password):
            messages.error(request, "Old password is incorrect")
        else:
            user.set_password(password)
            update_session_auth_hash(request, user)
            user.save()
            messages.success(request, "Password Changed")

        return redirect(request.path)

    return render(request, "settings_account.html", {"user": request.user})


def user(request, username=None):
    if username:
        try:
            profile = User.objects.get(username=username)
            return render(
                request, "user.html", {"profile": profile, "user": request.user}
            )
        except User.DoesNotExist:
            return redirect("/404")

    if request.user.is_authenticated:
        return render(
            request, "user.html", {"profile": request.user, "user": request.user}
        )
    return redirect("/login")


def product(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return redirect("/404")

    return render(request, "product.html", {"user": request.user, "product": product})


def add(request):
    if not request.user.is_authenticated:
        return redirect("/market")

    if request.POST:
        name = request.POST.get("product-name")
        price = request.POST.get("price")
        desc = request.POST.get("description")
        author = request.user
        if name and price:
            product = Product(name=name, author=author, price=price, desc=desc)
            product.save()
            return redirect(f"/product/{product.id}")
        else:
            messages.error("Must provide name and price")
            return redirect(request.path)

    return render(request, "add.html", {"user": request.user})


def update(request, id):
    product = get_object_or_404(Product, pk=id)

    if not request.user.is_authenticated or request.user != product.author:
        return redirect(f"/product/{id}")

    if request.POST:
        name = request.POST.get("product-name")
        price = request.POST.get("price")
        desc = request.POST.get("description")

        if name and price:
            product.name = name
            product.price = price
            product.desc = desc
            if request.user == product.author:
                product.save()
            return redirect(f"/product/{id}")
        else:
            messages.error("Must provide name and price")
            return redirect(request.path)

    return render(request, "update.html", {"user": request.user, "product": product})


def delete(request, id):
    product = get_object_or_404(Product, pk=id)

    if not request.user.is_authenticated or request.user != product.author:
        return redirect(f"/product/{id}")

    product.delete()
    return redirect("/market")


def market(request):
    products = Product.objects.all()
    return render(request, "market.html", {"user": request.user, "products": products})
