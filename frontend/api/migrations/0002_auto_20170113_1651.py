# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-13 15:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked', models.BooleanField(default=False)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Article')),
            ],
        ),
        migrations.CreateModel(
            name='TweetClusterAttributes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='TweetClusterAttributeValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('val', models.DecimalField(decimal_places=6, max_digits=10)),
                ('attr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.TweetClusterAttributes')),
            ],
        ),
        migrations.CreateModel(
            name='TweetClusterMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributes', models.ManyToManyField(to='api.TweetClusterAttributeValue')),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Cluster')),
                ('tweet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Tweet')),
            ],
        ),
        migrations.RemoveField(
            model_name='tweetcluster',
            name='article',
        ),
        migrations.RemoveField(
            model_name='tweetcluster',
            name='tweets',
        ),
        migrations.DeleteModel(
            name='TweetCluster',
        ),
        migrations.AddField(
            model_name='cluster',
            name='tweets',
            field=models.ManyToManyField(through='api.TweetClusterMembership', to='api.Tweet'),
        ),
    ]
