from django.contrib import admin

from .models import Cart, Comment, Product, User

admin.site.register(Cart)
admin.site.register(Comment)
admin.site.register(Product)
admin.site.register(User)
