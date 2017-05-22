# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0055_Make entities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverable',
            name='originator_new',
            field=models.ForeignKey(verbose_name='Originator', to='accounts.Entity'),
        ),
    ]
