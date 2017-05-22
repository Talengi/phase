# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.core.files.storage
import privatemedia.fields
import reviews.fileutils
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(default='reviewer', max_length=8, verbose_name='Role', choices=[('reviewer', 'Reviewer'), ('leader', 'Leader'), ('approver', 'Approver')])),
                ('revision', models.PositiveIntegerField(verbose_name='Revision')),
                ('due_date', models.DateField(null=True, verbose_name='Review due date', blank=True)),
                ('docclass', models.IntegerField(default=1, verbose_name='Class', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])),
                ('reviewed_on', models.DateTimeField(null=True, verbose_name='Reviewed on', blank=True)),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('comments', privatemedia.fields.PrivateFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=reviews.fileutils.review_comments_file_path, null=True, verbose_name='Comments', blank=True)),
                ('document', models.ForeignKey(verbose_name='Document', to='documents.Document')),
                ('reviewer', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Reviews',
            },
        ),
        migrations.AlterIndexTogether(
            name='review',
            index_together=set([('reviewer', 'document', 'revision', 'role')]),
        ),
    ]
