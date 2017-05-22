# -*- coding: utf-8 -*-


from django.db import models, migrations
import default_documents.validators


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0002_auto_20150811_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverable',
            name='sequential_number',
            field=models.CharField(default='0001', help_text='Select a four digit number', max_length=4, verbose_name='sequential Number', validators=[default_documents.validators.StringNumberValidator(length=4)]),
        ),
        migrations.AlterField(
            model_name='correspondence',
            name='sequential_number',
            field=models.CharField(default='0001', help_text='Type in a four digit number', max_length=4, verbose_name='sequential Number', validators=[default_documents.validators.StringNumberValidator(length=4)]),
        ),
        migrations.AlterField(
            model_name='minutesofmeeting',
            name='sequential_number',
            field=models.CharField(default='0001', help_text='Type in a four digit number', max_length=4, verbose_name='sequential Number', validators=[default_documents.validators.StringNumberValidator(length=4)]),
        ),
    ]
