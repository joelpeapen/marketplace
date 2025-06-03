from uuid import uuid4
from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(max_length=254)
    is_email_confirmed = models.BooleanField(default=False)
    pic = models.ImageField(
        upload_to="images/profiles/", default="images/profiles/profile_default.png"
    )
    purchases = models.ManyToManyField("History", related_name="products_bought")
    bio = models.TextField()


class Product(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField()
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(default=0)
    creation_date = models.DateTimeField()
    modify_date = models.DateTimeField()
    image = models.ImageField(upload_to="images/", default="images/default.png")
    stock = models.IntegerField(default=0)
    tags = models.ManyToManyField("Tag", related_name="product_tags")
    carters = models.ManyToManyField("User", related_name="carted_users")
    buyers = models.ManyToManyField("User", related_name="buyers")

    def is_bought(self, user):
        return user.purchases.filter(pid=self.id).exists()

    def make_rating(self):
        r = Comment.objects.filter(product=self).aggregate(average=Avg("rating"))
        self.rating = r["average"] or 0
        self.save()


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)


class History(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="history_authors")
    pid = models.IntegerField(default=0)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cart_status = models.BooleanField()
    date = models.DateField(auto_now_add=True)

    @classmethod
    def status_remove(self):
        History.objects.all().update(cart_status=False)


class Comment(models.Model):
    text = models.TextField()
    creation_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)


class Cart(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, primary_key=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def get_items(self):
        return self.cartitem_set.all()

    def get_item(self, p):
        try:
            item = self.cartitem_set.get(product=p)
        except CartItem.DoesNotExist:
            return None
        return item

    def has_item(self, p):
        return self.cartitem_set.filter(product=p).exists()

    def add_item(self, p, q):
        item = CartItem.objects.create(
            cart=self, product=p, quantity=q, total=p.price * q
        )
        self.total = 0
        for item in self.get_items():
            self.total += item.total

        self.save()
        p.carters.add(self.user)

    def remove_item(self, p):
        item = CartItem.objects.get(cart=self, product=p)
        self.total -= item.total
        item.delete()
        self.save()
        p.carters.remove(self.user)

    def checkout(self):
        History.status_remove()
        for item in self.get_items():
            h = History.objects.create(
                user=self.user,
                username=self.user.username,
                author=item.product.author,
                pid=item.product.id,
                name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
                total=item.product.price * item.quantity,
                cart_status=True,
            )
            self.user.purchases.add(h)
            item.product.buyers.add(self.user)
            item.product.stock -= item.quantity
            item.product.save()
            self.remove_item(item.product)

    @classmethod
    def update_product(self, p):
        users = User.objects.filter(cart__cartitem__product=p)

        for user in users:
            cart = user.cart
            item = cart.get_item(p)
            if item:
                prev = item.total
                new = item.product.price * item.quantity
                item.total = new
                item.save()

                cart.total += new
                cart.total -= prev
            cart.save()


class CartItem(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)


class EmailConfirmationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
