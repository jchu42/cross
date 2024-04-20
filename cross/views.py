import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
#from django.http import HttpResponse
#from django.http import Http404
#from django.template import loader
from .models import UserData
from .forms import LoginForm, RegisterForm, PuzzleBox
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .crossgen import CrossGen

gen = CrossGen(3)
max_gen_attempts = 10

def index(request):
    cnt = 0
    while cnt < max_gen_attempts:
        try:
            spacingx, spacingy, length, arr, hintsacross, hintsdown = gen.generate_puzzle()
            break
        except Exception as e:
            print(e)
            cnt += 1

    context={"puzzle":PuzzleBox(spacingx, spacingy, length, arr),}
    print("Solution: ", arr)
    hintsx = []
    hintsy = []
    for y, hint in enumerate(hintsacross):
        hintsy.append(str(y + spacingy + 1) + "-" + hint[0] + ": " + hint[1])
    for x, hint in enumerate(hintsdown):
        hintsx.append(str(x + spacingx + 1) + "-" + hint[0] + ": " + hint[1])
    context["hintsx"] = hintsx
    context["hintsy"] = hintsy

    if request.user.is_authenticated:
        authenticated_user = User.objects.get(username=request.user)
        data = authenticated_user.userdata

        data.current_cross = json.dumps(arr)
        data.crosses_started += 1
        data.save()

        context["user"] = authenticated_user
        context["data"] = data
        return render(request, "cross/index.html", context)
    else:
        context["user"] = ""
        return render(request, "cross/index.html", context)
    
def solve(request):
    if request.method!="POST":
        return HttpResponse("Only POST accepted")
    if request.user.is_authenticated:
        puzzleResults = PuzzleBox(data=request.POST) # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        if puzzleResults.is_valid():
            authenticated_user = User.objects.get(username=request.user)
            data = authenticated_user.userdata
            puzzle = data.current_cross
            puzzle = json.loads(puzzle)
            print("Saved Solution: ", puzzle)

            print ("Received Solution:")
            for y, line in enumerate(puzzle):
                for x, char in enumerate(line):
                    coords = str(x) + "," + str(y)
                    print(puzzleResults.cleaned_data[coords], end='')
                print()
            # check fields
            for y, line in enumerate(puzzle):
                for x, char in enumerate(line):
                    coords = str(x) + "," + str(y)
                    if char != "_":
                        if char != puzzleResults.cleaned_data[coords]:
                            # incorrect
                            print()
                            return HttpResponse("""Incorrect! <a href="/">New Game?</a>""")
                print()
            data.crosses_completed += 1
            data.save()
            return HttpResponse("""EZ. <a href="/">New Game?</a>""")
        print (puzzleResults.errors)
        return HttpResponse("""Gave up already? <a href="/">New Game?</a>""")
    return HttpResponse("""Not Logged In! <a href="/login">Login</a> <a href="/register">Register</a> <a href="/">Home</a>""")

def user_view(request, username):
    user = User.objects.get(username=username)
    data = user.userdata

    if data is None or data.crosses_started == 0:
        percent = "-"
    else:
        percent = str(int(data.crosses_completed/data.crosses_started*100)) + "%"

    context={"userdata": data, "username": username, "completionrate": percent}
    return render(request, "cross/user.html", context)

def login_view(request):
    if request.method=="POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            # https://docs.djangoproject.com/en/5.0/topics/auth/default/#authentication-in-web-requests
            login(request, user)
            # generate tokens and stuff?
            return HttpResponse("""Logged In.<a href="/">Home</a>""")
    else:
        form = LoginForm()
    return render(request, "cross/login.html", {"form": form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            new_user = User.objects.create_user(username=username, password=password)
            new_user.save()
            data = UserData(user=new_user, crosses_started=0, crosses_completed=0)
            data.save()
            return HttpResponse("""Registered. <a href="/login">Login</a> <a href="/">Home</a>""")
    else:
        form = RegisterForm()
    return render(request, "cross/register.html", {"form": form})

def logout_view(request):
    logout(request)
    return HttpResponse("""Logged Out.<a href="/">Home</a>""")

# def get_puzzle(request):
#     if request.method == "GET":
#         return HttpResponse(gen.generate_cross())