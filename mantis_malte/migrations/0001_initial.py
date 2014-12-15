# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('dingos', '0003_vio2fvalue'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FactTerm2Weight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('assignment_name', models.ForeignKey(related_name=b'aname', to='mantis_malte.AssignmentName')),
                ('fact_term', models.ForeignKey(related_name=b'weight_set', to='dingos.FactTerm')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='factterm2weight',
            unique_together=set([('fact_term', 'assignment_name')]),
        ),
    ]
