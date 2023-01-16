from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages


def login(request):
    form_name = request.POST.get('form_name')
    if request.method == "POST":
        if form_name == 'admin_form':
            email = request.POST['admin_email']
            password = request.POST['admin_password']
            username = User.objects.filter(email=email)[0].username
            user = auth.authenticate(request, username=username, password=password)
            if user.is_superuser: 
                auth.login(request, user)
                return redirect("/main/")
            else:           
                return render(request, "accounts/login.html")
        elif form_name == 'stuff_form':
            email = request.POST['stuff_email']
            password = request.POST['stuff_password']
            username = User.objects.filter(email=email)[0].username
            user = auth.authenticate(request, username=username, password=password)
            if user.is_staff:
                auth.login(request, user)
                return redirect("/main/")
            else:           
                return render(request, "accounts/login.html")
    return render(request, "accounts/login.html")



def logout(request):
    auth.logout(request)
    return redirect("/main/")