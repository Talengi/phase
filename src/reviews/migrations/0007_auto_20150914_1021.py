# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_auto_20150908_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='status',
            field=models.CharField(default='pending', max_length=30, verbose_name='Status', choices=[('void', ''), ('pending', 'Pending'), ('progress', 'In progress'), ('reviewed', 'Reviewed without comments'), ('commented', 'Reviewed with comments'), ('not_reviewed', 'Not reviewed')]),
        ),
    ]
