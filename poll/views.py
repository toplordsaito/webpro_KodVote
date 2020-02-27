from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.decorators import login_required
from .models import Poll
from datetime import datetime
from time import time
from dateutil.parser import parse
# Create your views here.


@login_required
def home(request):
    polls = Poll.objects.all()
    return render(request, 'poll/homepage.html', {'title': "Welcome to Poll App", 'polls': polls})


@login_required
def user_poll(request):
    polls = Poll.objects.filter(create_by=request.user)
    return render(request, 'poll/homepage.html', {'title': "My Poll", 'polls': polls})


@login_required
def createPoll(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        detail = request.POST.get('detail')
        start_date = checkDate(request.POST.get('start_date'))
        end_date = checkDate(request.POST.get('end_date'))
        password = request.POST.get('password', None)
        picture = request.FILES.get('picture', None)
        print(request.POST)

        # rename picture
        if picture:
            ext = '.' + picture.name.split('.')[-1]
            picture.name = str(time()) + ext

        poll = Poll.objects.create(subject=subject, detail=detail, start_date=start_date,
                    end_date=end_date, password=password, create_by=request.user, picture=picture)
        return redirect('home')

    return render(request, 'poll/create.html')


@login_required
def deletePoll(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    if poll.create_by == request.user:
        poll.delete()
    return redirect(to='home')


def checkDate(dateString):
    try:
        parse(dateString)
    except ValueError:
        dateString = datetime.now().isoformat(timespec='minutes')
    return dateString
