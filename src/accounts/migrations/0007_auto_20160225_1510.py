# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20160208_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='type',
            field=models.CharField(default='contractor', max_length=80, verbose_name='Type', choices=[('contractor', 'Contractor'), ('supplier', 'Supplier'), ('originator', 'Originator'), ('other', 'Other')]),
        ),
    ]
