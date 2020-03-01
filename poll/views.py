from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.decorators import login_required
from .models import Poll, Poll_Choice, Poll_Vote
from datetime import datetime
from time import time
from dateutil.parser import parse
from django.views.decorators.http import require_POST
import json
import random
import pytz
utc = pytz.UTC
# Create your views here.


@login_required
def home(request):
    polls = Poll.objects.all()
    closed = polls.filter(end_date__lte=datetime.now().replace(tzinfo=utc))
    avaliable = polls.filter(end_date__gt=datetime.now().replace(tzinfo=utc))
    return render(request, 'poll/homepage.html', {'title': "Welcome to Poll App", 'closed': closed, 'avaliable': avaliable})


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
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        return redirect("home")

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
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        return redirect("home")

    if poll.create_by == request.user:
        poll.delete()
    return redirect(to='home')


@login_required
def createChoice(request, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        return redirect("home")
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
    try:
        choice = Poll_Choice.objects.get(pk=choice_id)
    except Poll_Choice.DoesNotExist:
        return redirect("home")

    if choice.poll_id.create_by == request.user:
        choice.delete()
    return redirect(to='poll_update', poll_id=choice.poll_id.id)


@login_required
def viewPoll(request, poll_id, ignorePassword=False):
    print(ignorePassword)
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        return redirect("home")
    context = {'poll': poll}
    if poll.password and not ignorePassword:
        password = request.POST.get('password')
        if not password:
            return render(request, 'poll/password.html')
        elif password != poll.password:
            return render(request, 'poll/password.html', {"error": "password incorrect"})

    choices = Poll_Choice.objects.filter(poll_id=poll_id)
    context['choices'] = choices
    if poll.is_expire:
        context['answer'] = calAnswerPoll(choices)
    try:
        vote = Poll_Vote.objects.get(poll_id=poll_id, vote_by=request.user)
        context['myChoice'] = vote
    except Poll_Vote.DoesNotExist:
        pass
    return render(request, 'poll/view_poll.html', context)


@login_required
@require_POST
def votePoll(request, poll_id):
    choice = request.POST.get('choice')
    try:
        poll = Poll.objects.get(pk=poll_id)
        choice = Poll_Choice.objects.get(pk=choice, poll_id=poll)
    except Poll_Choice.DoesNotExist:
        return redirect('home')
    except Poll.DoesNotExist:
        return redirect('home')
    try:
        vote = Poll_Vote.objects.get(vote_by=request.user, poll_id=poll)
        vote.choice_id = choice
        vote.save()
    except Poll_Vote.DoesNotExist:
        Poll_Vote.objects.create(vote_by=request.user,
                                 poll_id=poll, choice_id=choice)
    return viewPoll(request, poll_id, True)


def calAnswerPoll(choices):
    allScore = sum(i.getScore for i in choices)
    data = []
    label = []
    color = []
    ans = []
    for choice in choices:
        choiceScore = choice.getScore
        data.append(choiceScore)
        label.append(choice.subject)
        color.append(
            "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]))
        ans.append({'choice': choice, 'score': choiceScore,
                    'percent': choiceScore/allScore*100})
    summary = {'data': data, 'label': label, 'color': color}
    summary = json.dumps(summary,  ensure_ascii=False)
    answer = {'summary': summary, 'ans': ans}
    return answer


def checkDate(dateString):
    try:
        parse(dateString)
    except ValueError:
        dateString = datetime.now().isoformat(timespec='minutes')
    return dateString
