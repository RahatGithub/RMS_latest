from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from main.models import Teacher

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        is_admin = request.POST['is_admin']
        print(email, password, is_admin)
        if is_admin == 'on':
            try:
                User.objects.get(email=email, password=password)
                return HttpResponse("logged in as admin")         
            except:           
                return HttpResponse("couldn't find such user (admin)")
        else:
            try:
                Teacher.objects.get(email=email, code=password)
                return HttpResponse("logged in as stuff...now go to teacher's dashboard")
            except:
                return HttpResponse("couldn't find such user")
    
    return render(request, "accounts/login.html")



def logout(request):
    auth.logout(request)
    return redirect("/main/")