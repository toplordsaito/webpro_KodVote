from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, localtime, _get_timezone_name
from datetime import datetime
import pytz
utc = pytz.UTC


class Poll(models.Model):
    subject = models.CharField(max_length=100)
    detail = models.TextField(null=True, blank=True)
    picture = models.ImageField(null=True, upload_to='images/poll')
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    password = models.CharField(max_length=32, null=True)
    create_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    create_date = models.DateTimeField(auto_now=True)

    @property
    def is_expire(self):
        return datetime.now().replace(tzinfo=utc) > self.end_date

    @property
    def get_timeleft(self):
        now = datetime.now().replace(tzinfo=utc)
        dif = self.end_date - now
        dif = dif.seconds
        string = "สิ้นสุดในอีก "
        if now > self.end_date:
            string = "โพลสิ้นสุดแล้ว"
        elif dif > 86400:
            string += str(dif//86400) + " วัน"
        elif dif > 3600:
            string += str(dif//3600) + " ชั่วโมง"
        elif dif > 60:
            string += str(dif//60) + " นาที"
        else:
            string += str(dif) + " วินาที"
        return string

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
