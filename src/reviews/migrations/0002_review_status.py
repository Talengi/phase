# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='status',
            field=models.CharField(default='pending', max_length=30, verbose_name='Status', choices=[('pending', 'Pending'), ('progress', 'In progress'), ('reviewed', 'Reviewed without comments'), ('commented', 'Reviewed with comments'), ('not_reviewed', 'Not reviewed')]),
        ),
    ]
