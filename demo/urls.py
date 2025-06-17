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

from app import views, utils

handler400 = "app.views.err"
handler403 = "app.views.err"
handler404 = "app.views.err"
handler500 = "app.views.e500"

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path('', views.index, name='index'),
    path("about/", views.about, name="about"),
    path("register/", views.register.as_view(), name="register"),
    path("login/", views.login_user.as_view(), name="login"),
    path("logout/", views.logout_user.as_view(), name="logout"),
    path("user/", views.user.as_view(), name="user"),
    path("user/settings/", views.settings.as_view(), name="settings"),
    path("user/settings/account/", views.settings_account.as_view(), name="settings-account"),
    path("user/settings/notifications/", views.settings_notify.as_view(), name="settings-notify"),
    path("user/delete/", views.delete_user.as_view(), name="delete-user"),
    path("user/<str:username>/", views.user.as_view(), name="user"),
    path("market/", views.market.as_view(), name="market"),
    path("product/<int:id>/", views.product.as_view(), name="product"),
    path("product/add/", views.add.as_view(), name="product-add"),
    path("product/update/<int:id>/", views.update.as_view(), name="product-update"),
    path("product/delete/<int:id>/", views.delete.as_view(), name="product-del"),
    path("comment/<int:id>", views.comment_add.as_view(), name="comment-add"),
    path("comment/update/<int:id>", views.comment_update.as_view(), name="comment-update"),
    path("comment/delete/<int:id>", views.comment_delete.as_view(), name="comment-del"),
    path("cart/", views.cart.as_view(), name="cart"),
    path("cart/add/<int:id>", views.cart_add.as_view(), name="cart-add"),
    path("cart/delete/<int:id>", views.cart_delete.as_view(), name="cart-del"),
    path("cart/update/<int:id>", views.cart_update.as_view(), name="cart-update"),
    path("checkout/", views.checkout.as_view(), name="checkout"),
    path("sales/", views.sales.as_view(), name="sales"),
    path("sales/plot/", utils.sales_plot, name="sales-plot"),
    path("purchases/", views.purchases.as_view(), name="purchases"),
    path("buyers/<int:id>", views.buyers.as_view(), name="buyers"),
    path("tags/<str:name>/", views.tags.as_view(), name="tags"),
    path("tags/add/<int:id>/", views.tag_add.as_view(), name="tag-add"),
    path("tags/delete/<int:pid>/<int:tid>/", views.tag_delete.as_view(), name="tag-delete"),
    path("search/", views.search.as_view(), name="search"),
    path("send-email-confirm/", views.send_email_confirm, name="send-email-confirm"),
    path("email-confirm/", views.set_email_confirm, name="set-email-confirm"),
    path("email-change/", views.email_change, name="email-change"),
    path("email-change-confirm/", views.set_email_change_confirm, name="email-change-confirm"),
    path("pass-mail/", views.pass_mail.as_view(), name="pass-mail"),
    path("passreset", views.pass_reset.as_view(), name="pass-reset"),
    path("send-pass-mail-confirm/", views.send_pass_mail_confirm, name="send-pass-mail-confirm"),
    path("set-password-confirm/", views.set_password_confirm, name="set-password-confirm"),
    path("report/", views.report.as_view(), name="report")
]
