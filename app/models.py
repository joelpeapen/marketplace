from django.db import models

class Email(models.Model):
    email = models.EmailField()

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.OneToOneField(Email, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)

class Product(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(max_length=10)
    creation_date = models.DateField(auto_now_add=True)

class Comment(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total = models.DecimalField(max_digits=10, decimal_places=2)
