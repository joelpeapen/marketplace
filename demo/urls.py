"""
URL configuration for demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path('', views.index, name='index'),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("user/", views.user),
    path("user/settings/", views.settings, name="settings"),
    path("user/settings/account/", views.settings_account, name="settings-account"),
    path("user/<str:username>/", views.user, name="user"),
    path("market/", views.market, name="market"),
    path("product/<int:id>/", views.product, name="product"),
    path("product/add/", views.add, name="product-add"),
    path("product/update/<int:id>/", views.update, name="product-update"),
    path("product/delete/<int:id>/", views.delete, name="product-del"),
    path("comment/<int:id>", views.comment_add, name="comment-add"),
    path("comment/update/<int:id>", views.comment_update, name="comment-update"),
    path("comment/delete/<int:id>", views.comment_delete, name="comment-del"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:id>", views.cart_add, name="cart-add"),
    path("cart/delete/<int:id>", views.cart_delete, name="cart-del"),
    path("cart/update/<int:id>", views.cart_update, name="cart-update"),
    path("checkout/", views.checkout, name="checkout"),
    path("purchases/", views.purchases, name="purchases"),
]
