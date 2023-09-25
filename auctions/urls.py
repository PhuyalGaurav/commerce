from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing", views.listit, name='listit' ),
    path("listing/<int:listitem>",views.listitem, name='listitem'),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlistadd/<int:listid>", views.watchlistadd, name="watchlistadd"),
    path("category", views.categories, name="categories"),
    path("category/<str:category>", views.categorieslist, name="categorylist"),
    path("addbid/<int:listid>", views.addbid, name="addbid"),
    path("addcomment/<int:listid>", views.addcomment, name="addcomment"),
    path("closebid/<int:listid>", views.closebid, name="closebid"),
    path("winnings", views.winnings, name="winnings")
]
