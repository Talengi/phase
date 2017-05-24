# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0037_auto_20160203_1240'),
    ]

    operations = [
        migrations.AddField(
            model_name='minutesofmeeting',
            name='contract_number_new',
            field=models.CharField(default='XYZ', max_length=50, verbose_name='Contract Number'),
            preserve_default=False,
        ),
    ]
