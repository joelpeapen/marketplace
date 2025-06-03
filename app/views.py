from datetime import datetime
from django.views import View
from django.db.models import Q, Count
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from app.utils import send_confirmation_email, send_purchase_email, send_purchase_email_seller
from app.models import (
    Cart,
    Comment,
    Product,
    User,
    Tag,
    History,
    EmailConfirmationToken,
)


def err(request, exception):
    return render(request, exception + ".html", {"e": exception, "user": request.user})


def e500(request):
    return render(request, "500.html", {"user": request.user})


def index(request):
    return render(request, "index.html", {"user": request.user})


def about(request):
    return render(request, "about.html", {"user": request.user})


def check_login(request, id=None):
    if id:
        if not request.user.is_authenticated:
            return redirect(f"/product/{id}")
    else:
        if not request.user.is_authenticated:
            return redirect("/login")


class register(View):
    def get(self, request):
        return render(request, "register.html", {"user": request.user})

    def post(self, request):
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
                    username=username,
                    email=email,
                    password=password,
                    date_joined=datetime.utcnow(),
                )
                Cart.objects.create(user=user, total=0)

                token = EmailConfirmationToken.objects.create(user=user)
                send_confirmation_email(email=user.email, token_id=token.pk)

                return render(
                    request, "email_confirm.html", {"new": True, "email": email}
                )
        else:
            messages.error(request, "All fields must be filled")
            return redirect("/register")


class login_user(View):
    def get(self, request):
        return render(request, "login.html", {"user": request.user})

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_email_confirmed:
                    login(request, user)
                    return redirect("/user")
                else:
                    return render(request, "email_confirm.html", {"user": user})
            else:
                messages.error(request, "Username or password is incorrect")
                return redirect("/login")
        else:
            messages.error(request, "All fields must be filled")


class logout_user(View):
    def get(self, request):
        check_login(request)

        logout(request)
        return redirect("/login")


class delete_user(View):
    def post(self, request):
        check_login(request)

        n = request.user.username
        request.user.delete()
        messages.success(request, f"User {n} has been deleted")
        return redirect("/register")


class settings(View):
    def get(self, request):
        check_login(request)
        return render(request, "settings.html", {"user": request.user})

    def post(self, request):
        check_login(request)

        username = request.POST.get("username")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        pic = request.FILES.get("pic")
        bio = request.POST.get("bio")

        user = request.user
        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, "A user with this username already exists")
                return redirect("/user/settings")
            user.username = username

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


class settings_account(View):
    def get(self, request):
        check_login(request)
        return render(request, "settings_account.html", {"user": request.user})

    # to change password
    def post(self, request):
        check_login(request)

        user = request.user
        password = request.POST.get("password")
        old_password = request.POST.get("old-password")
        confirm = request.POST.get("confirm-pw")

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
        elif password == old_password == confirm:
            messages.error(request, "Thats the same password")
        else:
            user.set_password(password)
            update_session_auth_hash(request, user)
            user.save()
            messages.success(request, "Password Changed")

        return redirect("/user/settings/account")


class user(View):
    def get(self, request, username=None):
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
            products = Product.objects.filter(
                author=request.user, stock__gt=0
            ).order_by("-rating")
            return render(
                request,
                "user.html",
                {"profile": request.user, "user": request.user, "products": products},
            )
        return redirect("/login")


class product(View):
    def get(self, request, id):
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
            cart = get_object_or_404(Cart, pk=request.user.pk)
            data["cart"] = cart
            data["in_cart"] = cart.has_item(product)
            data["cart_item"] = cart.get_item(product)
            data["is_bought"] = product.is_bought(request.user)
            data["buycount"] = request.user.buyers.count()

        return render(request, "product.html", data)


class add(View):
    def get(self, request):
        check_login(request)
        return render(request, "add.html", {"user": request.user})

    def post(self, request):
        check_login(request)

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
            date = datetime.utcnow()
            data = {
                "name": name,
                "author": author,
                "price": price,
                "stock": stock,
                "desc": desc,
                "creation_date": date,
                "modify_date": date,
            }
            if img:
                data["image"] = img

            print(data)

            product = Product(**data)
            product.save()
            return redirect(f"/product/{product.id}")
        else:
            messages.error(request, "Must provide name and price")
            return redirect(request.META.get("HTTP_REFERER"))


class update(View):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)

        if not request.user.is_authenticated or request.user != product.author:
            return redirect(f"/product/{id}")

        return render(
            request, "update.html", {"user": request.user, "product": product}
        )

    def post(self, request, id):
        product = get_object_or_404(Product, pk=id)

        if not request.user.is_authenticated or request.user != product.author:
            return redirect(f"/product/{id}")

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


class delete(View):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)

        if not request.user.is_authenticated or request.user != product.author:
            return redirect(f"/product/{id}")

        product.delete()
        return redirect("/market")


class market(View):
    def get(self, request):
        products = (
            Product.objects.filter(stock__gt=0)
            .annotate(num_buyers=Count("buyers"))
            .order_by("-rating", "-num_buyers")
        )
        return render(
            request, "market.html", {"user": request.user, "products": products}
        )


class comment_add(View):
    def post(self, request, id):
        check_login(request, id)

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


class comment_update(View):
    def post(self, request, id):
        check_login(request)

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


class comment_delete(View):
    def post(self, request, id):
        check_login(request)

        comment = get_object_or_404(Comment, pk=id)

        if comment.user == request.user:
            comment.delete()
            comment.product.make_rating()

        return redirect(f"/product/{comment.product.id}")


class cart(View):
    def get(self, request):
        check_login(request)

        cart = get_object_or_404(Cart, pk=request.user.pk)

        return render(
            request,
            "cart.html",
            {
                "user": request.user,
                "cart": cart,
                "cart_items": cart.get_items(),
            },
        )


class cart_add(View):
    def post(self, request, id):
        check_login(request, id)

        cart = get_object_or_404(Cart, pk=request.user)
        product = get_object_or_404(Product, id=id)
        quantity = int(request.POST.get("quantity"))

        if quantity < 0 or quantity > product.stock:
            messages.error(request, "invalid quantity")
            return redirect(request.META.get("HTTP_REFERER"))

        if not cart.has_item(product):
            cart.add_item(product, quantity)

        return redirect(request.META.get("HTTP_REFERER"))


class cart_delete(View):
    def post(self, request, id):
        check_login(request, id)

        cart = get_object_or_404(Cart, pk=request.user)
        product = get_object_or_404(Product, id=id)
        cart.remove_item(product)

        return redirect(request.META.get("HTTP_REFERER"))


class cart_update(View):
    def post(self, request, id):
        check_login(request, id)

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


class checkout(View):
    def get(self, request):
        check_login(request)
        return redirect("/user")

    def post(self, request):
        check_login(request)

        cart = get_object_or_404(Cart, user=request.user)
        cart.checkout()

        checked = request.user.purchases.filter(cart_status=True)
        count = checked.count()

        send_purchase_email(request.user.email, checked)

        for purchase in checked:
            send_purchase_email_seller(purchase.author.email, purchase)

        return render(
            request,
            "checkout.html",
            {"user": request.user, "purchased": checked, "count": count},
        )


class purchases(View):
    def get(self, request):
        check_login(request)

        return render(
            request,
            "purchased.html",
            {"user": request.user, "products": request.user.purchases.all()},
        )


class buyers(View):
    def get(self, request, id):
        check_login(request)

        product = Product.objects.get(pk=id)
        buyers = History.objects.filter(pid=id)

        return render(
            request,
            "buyers.html",
            {"user": request.user, "buyers": buyers, "product": product},
        )


class tags(View):
    def get(self, request, name):
        tags = Tag.objects.filter(name=name)
        products = set()

        for tag in tags:
            products.update(tag.product_tags.all())

        data = {
            "user": request.user,
            "products": list(products),
        }

        try:
            tag = tags[0]
            data["tag"] = tag
        except IndexError:
            return redirect("/404")

        return render(request, "tags.html", data)


class tag_add(View):
    def post(self, request, id):
        product = get_object_or_404(Product, pk=id)

        if not request.user.is_authenticated or request.user != product.author:
            messages.error(request, "only product author can add tags")
            return redirect(f"/product/{id}")

        tag_name = request.POST.get("tag")

        if tag_name:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            product.tags.add(tag)
        else:
            messages.error("Tag cannot be empty")

        return redirect(f"/product/{id}")


class tag_delete(View):
    def post(self, request, pid, tid):
        product = get_object_or_404(Product, pk=pid)

        if not request.user.is_authenticated or request.user != product.author:
            messages.error(request, "only product author can delete tags")
            return redirect(f"/product/{pid}")

        tag = get_object_or_404(Tag, pk=tid)
        product.tags.remove(tag)

        return redirect(f"/product/{pid}")


class search(View):
    def get(self, request):
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


def send_email_confirm(request):
    if request.POST:
        username = request.POST.get("user")
        if username:
            user = get_object_or_404(User, username=username)

        token, _ = EmailConfirmationToken.objects.get_or_create(user=user)
        send_confirmation_email(email=user.email, token_id=token.pk)
        messages.info(request, "Check your email for the verification link")
        return render(request, "email_confirm.html", {"is_email_confirmed": False})


# the email sends link to this
def set_email_confirm(request):
    if request.GET:
        token_id = request.GET.get("token_id", None)
        try:
            token = EmailConfirmationToken.objects.get(pk=token_id)
            user = token.user
            user.is_email_confirmed = True
            user.save()
            token.delete()
            data = {"is_email_confirmed": True}
            return render(request, "email_confirm.html", data)
        except EmailConfirmationToken.DoesNotExist:
            data = {"is_email_confirmed": False}
            return render(request, "email_confirm.html", data)


def email_change(request):
    if request.POST:
        check_login(request)

        user = request.user
        new_email = request.POST.get("email")
        print(f"NEW EMAIL: {new_email}")

        if User.objects.filter(email=new_email).exists():
            messages.error(request, "A user with this email already exists")
            return redirect("/user/settings/account")

        token, _ = EmailConfirmationToken.objects.get_or_create(user=user)
        send_confirmation_email(email=new_email, token_id=token.pk, change=True)
        return render(
            request, "email_confirm.html", {"change": True, "email": new_email}
        )


def set_email_change_confirm(request):
    if request.GET:
        token_id = request.GET.get("token_id", None)
        email = request.GET.get("email", None)
        print(f"RECEIVED TOKEN: {token_id}")
        print(f"RECEIVED EMAIL: {email}")
        try:
            token = EmailConfirmationToken.objects.get(pk=token_id)
            user = token.user
            print(f"RECEIVED USER: {user}")
            user.email = email
            print(f"SET THE EMAIL: {email}")
            user.save()
            token.delete()
            data = {"change": True, "is_email_confirmed": True}
            return render(request, "email_confirm.html", data)
        except EmailConfirmationToken.DoesNotExist:
            data = {"change": True, "is_email_confirmed": False}
            return render(request, "email_confirm.html", data)
