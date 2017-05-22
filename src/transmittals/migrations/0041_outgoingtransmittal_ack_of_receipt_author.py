# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transmittals', '0040_auto_20160209_0821'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='ack_of_receipt_author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Acknowledgment of receipt author', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
