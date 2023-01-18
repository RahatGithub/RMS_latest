from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from main.models import Teacher

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect("/main/")
        else:           
            messages.info(request, "Wrong username or password!")
            return render(request, "accounts/login.html") 
    return render(request, "accounts/login.html")



def logout(request):
    auth.logout(request)
    return redirect("/main/")