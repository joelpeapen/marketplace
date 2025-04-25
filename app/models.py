from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(primary_key=True, max_length=254)
    pic = models.ImageField(upload_to="images/profiles/", default="images/profiles/profile_default.png")
    purchases = models.ManyToManyField("History", related_name="products_bought")
    creation_date = models.DateField(auto_now_add=True)
    bio = models.TextField()

class Product(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField()
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(default=0)
    creation_date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to="images/", default="images/default.png")
    users = models.ManyToManyField("User", related_name="carted_users")
    stock = models.IntegerField(default=0)

    def is_bought(self, user):
        return user.purchases.filter(pid=self.id).exists()


class History(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
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
        p.users.add(self.user)

    def remove_item(self, p):
        item = CartItem.objects.get(cart=self, product=p)
        self.total -= item.total
        item.delete()
        self.save()
        p.users.remove(self.user)

    def checkout(self):
        History.status_remove()
        for item in self.get_items():
            h = History.objects.create(
                user=self.user,
                pid=item.product.id,
                name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
                total=item.product.price * item.quantity,
                cart_status=True,
            )
            self.user.purchases.add(h)
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
