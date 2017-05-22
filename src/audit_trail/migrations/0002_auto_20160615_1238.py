# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='verb',
            field=models.CharField(default='joined', max_length=128, verbose_name='Verb', choices=[('created', 'created'), ('edited', 'edited'), ('deleted', 'deleted'), ('joined', 'joined Phase'), ('started_review', 'started review'), ('cancelled_review', 'cancelled review'), ('reviewed', 'reviewed'), ('closed_reviewer_step', 'closed reviewer step'), ('closed_leader_step', 'closed leader step'), ('closed_approver_step', 'closed approver step'), ('sent_back_to_leader_step', 'sent review back to leader')]),
        ),
    ]
