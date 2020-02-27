from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Poll(models.Model):
    subject = models.CharField(max_length=100)
    detail = models.TextField(null=True, blank=True)
    picture = models.ImageField(null=True, upload_to='images/poll')
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    password = models.CharField(max_length=32, null=True)
    create_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    create_date = models.DateTimeField(auto_now=True)


class Poll_Choice(models.Model):
    subject = models.CharField(max_length=100)
    picture = models.ImageField(null=True, upload_to='images/choice')
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)


class Poll_Vote(models.Model):
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_id = models.ForeignKey(Poll_Choice, on_delete=models.CASCADE)
    vote_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
