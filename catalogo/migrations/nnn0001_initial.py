# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-21 03:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('notas', models.CharField(max_length=200)),
                ('imprint', models.CharField(max_length=200)),
                ('isbn', models.CharField(max_length=13)),
                ('Empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogo.Empresa')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='Producto',
            name='subject',
            field=models.ManyToManyField(to='catalogo.Subject'),
        ),
    ]
