# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0007_auto_20150914_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='status',
            field=models.CharField(default='pending', max_length=30, verbose_name='Status', choices=[('void', ''), ('pending', 'Pending'), ('progress', 'In progress'), ('reviewed', 'Reviewed'), ('commented', 'Reviewed'), ('not_reviewed', 'Not reviewed')]),
        ),
    ]
