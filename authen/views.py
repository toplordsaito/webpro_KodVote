from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError


def mylogin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(request.GET.get('next', '/'))
        else:
            # form = AuthenticationForm(request.POST)
            return render(request, 'login.html', {'username': username, 'error': 'wrong username or password'})
    else:
        return render(request, 'login.html')


def mylogout(request):
    logout(request)
    return HttpResponseRedirect('/')


def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        user, context = checkUser(request.POST)
        if user:
            user = authenticate(
                username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            context.update(request.POST)
            return render(request, 'signup.html', context)
    else:
        return render(request, 'signup.html')


def checkUser(form):
    user = User()
    context = {}
    user.username = form.get('username')
    user.firstname = form.get('firstname')
    user.lastname = form.get('lastname')
    user.email = form.get('email')
    password1 = form.get('password1')
    password2 = form.get('password2')
    if password1 and password2 and password1 == password2:
        user.set_password(password1)
    else:
        user = None
        context['error'] = "password is not match"
    try:
        if user:
            user.save()
            context['msg'] = "register succesfully"
    except IntegrityError:
        user = None
        context['error'] = "username is already exists"

    return user, context
