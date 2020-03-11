from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Poll, Poll_Choice, Poll_Vote
from datetime import datetime
from time import time
from dateutil.parser import parse
from django.views.decorators.http import require_POST
from django.db.models import Q


@login_required
def home(request, **kwargs):
    if kwargs.get('polls') == None:
        polls = Poll.objects.all()
    else:
        polls = kwargs['polls']
    closed = polls.filter(Q(end_date__lte=datetime.now()) | Q(is_active=False))
    avaliable = polls.filter(end_date__gt=datetime.now(), is_active=True)
    context = {}
    context['title'] = kwargs.get('title') or "Welcome to Poll App"
    context['closed'] = closed
    context['avaliable'] = avaliable
    return render(request, 'poll/homepage.html', context)


@login_required
def user_poll(request):
    polls = Poll.objects.filter(create_by=request.user)
    return home(request, polls=polls, title="My Polls")


@login_required
def createPoll(request):
    context = {'title': 'Create Poll'}
    if request.method == 'POST':
        poll = Poll()
        poll = checkPoll(poll, request)
        poll.create_by = request.user
        poll.save()
        context['title'] = "Update Poll"
        context['msg'] = "Create Successfuly"
        context['poll'] = poll
    return render(request, 'poll/poll_form.html', context)


@login_required
def updatePoll(request, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        return redirect("home")
    context = {}
    if request.method == 'POST' and poll.create_by == request.user:
        poll = checkPoll(poll, request)
        poll.save()
        context['msg'] = "Update Successfuly"
    context['title'] = 'Update Poll'
    context['poll'] = poll
    context['choices'] = Poll_Choice.objects.filter(poll_id=poll_id)
    return render(request, 'poll/poll_form.html', context)


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
def viewPoll(request, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        return redirect("home")

    context = {'poll': poll}

    choices = Poll_Choice.objects.filter(poll_id=poll_id)
    context['choices'] = choices
    if poll.is_expire:
        context['answer'] = poll.getAnswerPoll
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
        if poll.is_expire:
            return redirect('home')
        choice = Poll_Choice.objects.get(pk=choice, poll_id=poll)
    except Poll_Choice.DoesNotExist:
        return redirect('home')
    except Poll.DoesNotExist:
        return redirect('home')
    if poll.password:
        password = request.POST.get('password')
        context = {'choice': choice}
        if not password:
            return render(request, 'poll/password.html', context)
        elif password != poll.password:
            context['error'] = "password incorrect"
            return render(request, 'poll/password.html', context)

    try:
        vote = Poll_Vote.objects.get(vote_by=request.user, poll_id=poll)
        vote.choice_id = choice
        vote.save()
    except Poll_Vote.DoesNotExist:
        Poll_Vote.objects.create(vote_by=request.user,
                                 poll_id=poll, choice_id=choice)
    # return viewPoll(request, poll_id)
    return redirect('poll_view', poll_id=poll_id)


def checkPoll(poll, request):
    poll.subject = request.POST.get('subject')
    poll.detail = request.POST.get('detail')
    poll.start_date = checkDate(request.POST.get('start_date'))
    poll.end_date = checkDate(request.POST.get('end_date'))
    poll.password = request.POST.get('password')
    poll.is_active = request.POST.get('is_active') == "True"
    picture = request.FILES.get('picture', None)
    if picture:
        ext = '.' + picture.name.split('.')[-1]
        picture.name = str(time()) + ext
        poll.picture = picture
    return poll


def checkDate(dateString):
    try:
        dateString = parse(dateString)
        # print(date)
    except ValueError:
        dateString = datetime.now()  # .isoformat(timespec='minutes')
    return dateString
