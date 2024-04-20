from django.urls import path
from . import views

app_name = 'cross'
urlpatterns=[
    # 
    path("", views.index, name="index"),
    # /a
    path("user/<str:username>", views.user_view, name="user"),
    # /login
    path("login", views.login_view, name="login"),
    # /register
    path("register", views.register, name="register"),
    # /logout
    path("logout", views.logout_view, name="logout"),
    # /solve
    path("solve", views.solve, name="solve"),
]