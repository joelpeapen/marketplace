from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(primary_key=True, max_length=254)


class Product(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(default=0)
    creation_date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to="images/", default="images/default.png")
    users = models.ManyToManyField(User, related_name="carted_users")


class Comment(models.Model):
    text = models.TextField()
    creation_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
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

    @classmethod
    def update(self, p):
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
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
