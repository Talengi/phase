# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0002_auto_20160615_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='verb',
            field=models.CharField(default='joined', max_length=128, verbose_name='Verb', choices=[('created', 'created'), ('edited', 'edited'), ('deleted', 'deleted'), ('joined', 'joined Phase'), ('started_review', 'started review on'), ('cancelled_review', 'cancelled review on'), ('reviewed', 'reviewed'), ('closed_reviewer_step', 'closed reviewer step on'), ('closed_leader_step', 'closed leader step on'), ('closed_approver_step', 'closed approver step on'), ('sent_back_to_leader_step', 'sent review back to leader')]),
        ),
    ]
