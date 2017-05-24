# -*- coding: utf-8 -*-


from django.db import migrations, models
import metadata.fields


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0026_auto_20160203_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverable',
            name='contract_number_old',
            field=metadata.fields.ConfigurableChoiceField(max_length=15, null=True, verbose_name='Contract Number', list_index='CONTRACT_NBS', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='contractordeliverable',
            unique_together=set([('contract_number_old', 'originator', 'unit', 'discipline', 'document_type', 'sequential_number')]),
        ),
    ]
