from django.urls import path
from . import views

app_name = 'cross'
urlpatterns=[
    # /cross/
    path("", views.index, name="index"),
    # /cross/joe/
    path("<str:username>/", views.user_view, name="user"),
    # /cross/login
    path("login", views.login_view, name="login"),
    # /cross/register
    path("register", views.register, name="register"),
    # /cross/logout
    path("logout", views.logout_view, name="logout"),
    # /cross/solve
    path("solve", views.solve, name="solve"),
]