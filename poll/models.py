from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import datetime
import json
import random


class Poll(models.Model):
    subject = models.CharField(max_length=100)
    detail = models.TextField(null=True, blank=True)
    picture = models.ImageField(null=True, upload_to='images/poll')
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    password = models.CharField(max_length=32, null=True)
    create_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    create_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    @property
    def is_expire(self):
        return (datetime.now() > self.end_date) or not self.is_active

    @property
    def get_timeleft(self):
        now = datetime.now()
        dif = self.end_date - now
        day = dif.days
        dif = dif.seconds
        if self.is_expire:
            string = "โพลสิ้นสุดแล้ว"
        else:
            string = "สิ้นสุดในอีก "
            if day > 0:
                string += str(day) + " วัน"
            elif dif > 3600:
                string += str(dif//3600) + " ชั่วโมง"
            elif dif > 60:
                string += str(dif//60) + " นาที"
            else:
                string += str(dif) + " วินาที"
        return string

    @property
    def getAnswerPoll(self):
        choices = Poll_Choice.objects.filter(poll_id=self.id)
        allScore = sum(i.getScore for i in choices)
        allScore = max(1, allScore)
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
                        'percent': int(choiceScore/allScore*100)})
        summary = {'data': data, 'label': label, 'color': color}
        summary = json.dumps(summary,  ensure_ascii=False)
        answer = {'summary': summary, 'ans': ans}
        return answer

    class Meta:
        ordering = ['-end_date']


class Poll_Choice(models.Model):
    subject = models.CharField(max_length=100)
    picture = models.ImageField(null=True, upload_to='images/choice')
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)

    @property
    def getScore(self):
        answer = self.poll_vote_set.all()
        return len(answer)


class Poll_Vote(models.Model):
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_id = models.ForeignKey(
        Poll_Choice, on_delete=models.CASCADE, null=True)
    vote_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
