from datetime import datetime
from django.db.models import Q, Count
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from app.models import Cart, Comment, Product, User, Tag, History


def err(request, exception):
    return render(request, exception + ".html", {"e": exception, "user": request.user})


def e500(request):
    return render(request, "500.html", {"user": request.user})


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
                user = User.objects.create_user(
                    username=username, email=email, password=password, date_joined=datetime.utcnow()
                )
                Cart.objects.create(user=user, total=0)
                messages.success(request, "Registration successful")
                return redirect("/login")
        else:
            messages.error(request, "All fields must be filled")
            return redirect("/register")

    return render(request, "register.html", {"user": request.user})


def delete_user(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    if request.POST:
        n = request.user.username
        request.user.delete()
        messages.success(request, f"User {n} has been deleted")
        return redirect("/register")


def login_user(request):
    if request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
        else:
            messages.error(request, "All fields must be filled")

        if user:
            login(request, user)
            return redirect("/user")
        else:
            messages.error(request, "Username or password is incorrect")
            return redirect("/login")

    return render(request, "login.html", {"user": request.user})


def logout_user(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    logout(request)
    return redirect("/login")


def settings(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    if request.POST:
        email = request.POST.get("email")
        username = request.POST.get("username")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        pic = request.FILES.get("pic")
        bio = request.POST.get("bio")

        user = request.user
        if username and username != user.username:
            user.username = username

        if email and email != user.email:
            user.email = email

        if fname != user.first_name:
            user.first_name = fname

        if lname != user.last_name:
            user.last_name = lname

        if bio and bio != user.bio:
            user.bio = bio

        if pic:
            user.pic = pic

        user.save()
        messages.success(request, "Profile Updated")
        return redirect("/user/settings")

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

        return redirect("/user/settings/account")

    return render(request, "settings_account.html", {"user": request.user})


def user(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username)
        products = (
            Product.objects.filter(author=profile, stock__gt=0)
            .annotate(num_buyers=Count("buyers"))
            .order_by("-rating", "-num_buyers")
        )
        return render(
            request,
            "user.html",
            {"profile": profile, "user": request.user, "products": products},
        )

    # /user/ -> logged-in user's page
    if request.user.is_authenticated:
        products = Product.objects.filter(author=request.user, stock__gt=0).order_by(
            "-rating"
        )
        return render(
            request,
            "user.html",
            {"profile": request.user, "user": request.user, "products": products},
        )
    return redirect("/login")


def product(request, id):
    product = get_object_or_404(Product, pk=id)
    comments = Comment.objects.filter(product=id)
    tags = product.tags.all()

    data = {
        "user": request.user,
        "product": product,
        "comments": comments,
        "count": comments.count(),
        "tags": tags,
    }

    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, pk=request.user.email)
        data["cart"] = cart
        data["in_cart"] = cart.has_item(product)
        data["cart_item"] = cart.get_item(product)
        data["is_bought"] = product.is_bought(request.user)
        data["buycount"] = request.user.buyers.count()

    return render(request, "product.html", data)


def add(request):
    if not request.user.is_authenticated:
        return redirect("/market")

    if request.POST:
        name = request.POST.get("product-name")
        price = float(request.POST.get("price"))
        stock = int(request.POST.get("stock"))
        desc = request.POST.get("description")
        img = request.FILES.get("image")
        author = request.user

        if price < 0:
            messages.error(request, "invalid price")
            return redirect(request.META.get("HTTP_REFERER"))

        if stock <= 0:
            messages.error(request, "invalid stock")
            return redirect(request.META.get("HTTP_REFERER"))

        if name and price:
            data = {
                "name": name,
                "author": author,
                "price": price,
                "stock": stock,
                "desc": desc,
                "creation_date": datetime.utcnow(),
            }
            if img:
                data["image"] = img

            product = Product(**data)
            product.save()
            return redirect(f"/product/{product.id}")
        else:
            messages.error(request, "Must provide name and price")
            return redirect(request.META.get("HTTP_REFERER"))

    return render(request, "add.html", {"user": request.user})


def update(request, id):
    product = get_object_or_404(Product, pk=id)

    if not request.user.is_authenticated or request.user != product.author:
        return redirect(f"/product/{id}")

    if request.POST:
        name = request.POST.get("product-name")
        price = float(request.POST.get("price"))
        stock = int(request.POST.get("stock"))
        desc = request.POST.get("description")
        img = request.FILES.get("image")

        if price < 0:
            messages.error(request, "invalid price")
            return redirect(request.META.get("HTTP_REFERER"))

        if stock <= 0:
            messages.error(request, "invalid stock")
            return redirect(request.META.get("HTTP_REFERER"))

        if name and price:
            product.name = name
            product.price = price
            product.desc = desc
            product.stock = stock
            product.modify_date = datetime.utcnow()
            if img:
                product.image = img

            product.save()
            Cart.update_product(product)
            return redirect(f"/product/{id}")
        else:
            messages.error("Must provide name and price")
            return redirect(f"/product/update/{id}")

    return render(request, "update.html", {"user": request.user, "product": product})


def delete(request, id):
    product = get_object_or_404(Product, pk=id)

    if not request.user.is_authenticated or request.user != product.author:
        return redirect(f"/product/{id}")

    product.delete()
    return redirect("/market")


def market(request):
    products = (
        Product.objects.filter(stock__gt=0)
        .annotate(num_buyers=Count("buyers"))
        .order_by("-rating", "-num_buyers")
    )
    return render(request, "market.html", {"user": request.user, "products": products})


def comment_add(request, id):
    if not request.user.is_authenticated:
        return redirect(f"/product/{id}")

    if request.POST:
        text = request.POST.get("comment")
        rating = int(request.POST.get("rating"))
        product = Product.objects.get(pk=id)

        if not product.is_bought(request.user):
            messages.error("Must buy the product to comment")
            return redirect(f"/product/{id}")

        if text and rating:
            Comment.objects.create(
                text=text, user=request.user, product=product, rating=rating
            )
            product.make_rating()
            return redirect(f"/product/{id}")
        else:
            messages.error("Must add a comment and rating")
            return redirect(f"/product/{id}")

    return redirect(f"/product/{id}")


def comment_update(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    if request.POST:
        text = request.POST.get("comment")
        rating = int(request.POST.get("rating"))

        if text and rating:
            comment = get_object_or_404(Comment, product=id)
            comment.text = text
            comment.rating = rating
            comment.save()
            comment.product.make_rating()
            return redirect(f"/product/{id}")
        else:
            messages.error("Must add a comment and rating")
            return redirect(f"/product/{id}")

    return redirect(request.path.get("HTTP_REFERER"))


def comment_delete(request, id):
    if not request.user.is_authenticated:
        return redirect(request.path.get("HTTP_REFERER"))

    comment = get_object_or_404(Comment, pk=id)

    if request.POST:
        if comment.user == request.user:
            comment.delete()
            comment.product.make_rating()
        return redirect(f"/product/{comment.product.id}")

    return redirect(f"/product/{comment.product.id}")


def cart(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    cart = get_object_or_404(Cart, pk=request.user.email)

    return render(
        request,
        "cart.html",
        {
            "user": request.user,
            "cart": cart,
            "cart_items": cart.get_items(),
        },
    )


def cart_add(request, id):
    if not request.user.is_authenticated:
        return redirect(f"/product/{id}")

    if request.POST:
        cart = get_object_or_404(Cart, pk=request.user)
        product = get_object_or_404(Product, id=id)
        quantity = int(request.POST.get("quantity"))

        if quantity < 0 or quantity > product.stock:
            messages.error(request, "invalid quantity")
            return redirect(request.META.get("HTTP_REFERER"))

        if not cart.has_item(product):
            cart.add_item(product, quantity)

    return redirect(request.META.get("HTTP_REFERER"))


def cart_delete(request, id):
    if not request.user.is_authenticated:
        return redirect(f"/product/{id}")

    if request.POST:
        cart = get_object_or_404(Cart, pk=request.user)
        product = get_object_or_404(Product, id=id)
        cart.remove_item(product)

    return redirect(request.META.get("HTTP_REFERER"))


def cart_update(request, id):
    if not request.user.is_authenticated:
        return redirect(f"/product/{id}")

    if request.POST:
        cart = get_object_or_404(Cart, pk=request.user)
        product = get_object_or_404(Product, id=id)
        quantity = int(request.POST.get("quantity"))

        if quantity < 0 or quantity > 10:
            messages.error(request, "invalid quantity")
            return redirect(request.META.get("HTTP_REFERER"))

        item = cart.get_item(product)
        if item:
            item.quantity = quantity
            item.save()
            cart.update_product(product)

    return redirect(request.META.get("HTTP_REFERER"))


def checkout(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    if request.POST:
        cart = get_object_or_404(Cart, user=request.user)
        cart.checkout()

        checked = request.user.purchases.filter(cart_status=True)
        count = checked.count()

        return render(
            request,
            "checkout.html",
            {"user": request.user, "purchased": checked, "count": count},
        )

    return redirect("/user")


def purchases(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    return render(
        request,
        "purchased.html",
        {"user": request.user, "products": request.user.purchases.all()},
    )


def buyers(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    buyers = History.objects.filter(pid=id)

    return render(
        request,
        "buyers.html",
        {"user": request.user, "buyers": buyers, "product": buyers[0]},
    )


def tags(request, name):
    tags = Tag.objects.filter(name=name)
    products = set()

    for tag in tags:
        products.update(tag.product_tags.all())

    return render(
        request,
        "tags.html",
        {"user": request.user, "products": list(products), "tag": tags[0]},
    )


def tag_add(request, id):
    product = get_object_or_404(Product, pk=id)

    if not request.user.is_authenticated or request.user != product.author:
        messages.error(request, "only product author can add tags")
        return redirect(f"/product/{id}")

    if request.POST:
        tag_name = request.POST.get("tag")

        if tag_name:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            product.tags.add(tag)
        else:
            messages.error("Tag cannot be empty")

    return redirect(f"/product/{id}")


def tag_delete(request, pid, tid):
    product = get_object_or_404(Product, pk=pid)

    if not request.user.is_authenticated or request.user != product.author:
        messages.error(request, "only product author can delete tags")
        return redirect(f"/product/{pid}")

    if request.POST:
        tag = get_object_or_404(Tag, pk=tid)
        product.tags.remove(tag)

    return redirect(f"/product/{pid}")


def search(request):
    if request.GET:
        query = request.GET.get("query")
        username = request.GET.get("user", None)
        qf = Q(name__icontains=query) | Q(desc__icontains=query) & Q(stock__gt=0)

        if username:
            try:
                u = User.objects.get(username=username)
                qf &= Q(author=u)
            except User.DoesNotExist:
                u = None

        products = (
            Product.objects.filter(qf)
            .annotate(num_buyers=Count("buyers"))
            .order_by("-rating", "-num_buyers")
            .distinct()
        )

    return render(
        request,
        "search.html",
        {
            "query": query,
            "username": username,
            "products": products,
        },
    )
