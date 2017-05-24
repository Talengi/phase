# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0052_auto_20160224_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverable',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='default_documents.ContractorDeliverableRevision', null=True),
        ),
        migrations.AlterField(
            model_name='correspondence',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='default_documents.CorrespondenceRevision', null=True),
        ),
        migrations.AlterField(
            model_name='minutesofmeeting',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='default_documents.MinutesOfMeetingRevision', null=True),
        ),
    ]
