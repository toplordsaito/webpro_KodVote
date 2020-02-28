from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.decorators import login_required
from .models import Poll, Poll_Choice, Poll_Vote
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
    context = {'title': 'Create Poll'}
    if request.method == 'POST':
        subject = request.POST.get('subject')
        detail = request.POST.get('detail')
        start_date = checkDate(request.POST.get('start_date'))
        end_date = checkDate(request.POST.get('end_date'))
        password = request.POST.get('password', None)
        picture = request.FILES.get('picture', None)
        # rename picture
        if picture:
            ext = '.' + picture.name.split('.')[-1]
            picture.name = str(time()) + ext

        poll = Poll.objects.create(subject=subject, detail=detail, start_date=start_date,
                                   end_date=end_date, password=password, create_by=request.user, picture=picture)
        context['title'] = "Update Poll"
        context['msg'] = "Create Successfuly"
        context['poll'] = poll
    return render(request, 'poll/create.html', context)


@login_required
def updatePoll(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    context = {}
    if request.method == 'POST' and poll.create_by == request.user:
        poll.subject = request.POST.get('subject')
        poll.detail = request.POST.get('detail')
        poll.start_date = checkDate(request.POST.get('start_date'))
        poll.end_date = checkDate(request.POST.get('end_date'))
        poll.password = request.POST.get('password')
        picture = request.FILES.get('picture', None)
        if picture:
            ext = '.' + picture.name.split('.')[-1]
            picture.name = str(time()) + ext
            poll.picture = picture
        poll.save()
        context['msg'] = "Update Successfuly"
    context['title'] = 'Update Poll'
    context['poll'] = poll
    context['choices'] = Poll_Choice.objects.filter(poll_id=poll_id)
    return render(request, 'poll/create.html', context)


@login_required
def deletePoll(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    if poll.create_by == request.user:
        poll.delete()
    return redirect(to='home')


@login_required
def createChoice(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    if request.method == 'POST' and poll.create_by == request.user:
        subject = request.POST.get('subject')
        picture = request.FILES.get('picture', None)
        if picture:
            ext = '.' + picture.name.split('.')[-1]
            picture.name = str(poll_id) + "_" + str(time()) + ext
        choice = Poll_Choice.objects.create(
            subject=subject, picture=picture, poll_id=poll)
        return redirect(to='poll_update', poll_id=poll_id)
    return redirect('home')


@login_required
def deleteChoice(request, choice_id):
    choice = Poll_Choice.objects.get(pk=choice_id)
    if choice.poll_id.create_by == request.user:
        choice.delete()
    return redirect(to='poll_update', poll_id=choice.poll_id.id)


@login_required
def viewPoll(request, poll_id):
    return render(request, 'poll/view_poll.html')


def checkDate(dateString):
    try:
        parse(dateString)
    except ValueError:
        dateString = datetime.now().isoformat(timespec='minutes')
    return dateString
