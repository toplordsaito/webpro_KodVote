# Generated by Django 3.0.3 on 2020-02-28 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0004_auto_20200227_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll_vote',
            name='choice_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='poll.Poll_Choice'),
        ),
    ]
