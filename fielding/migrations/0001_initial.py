# Generated by Django 5.1 on 2024-08-30 11:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('match', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fielding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catches', models.IntegerField(blank=True, default=0, null=True)),
                ('stumpings', models.IntegerField(blank=True, default=0, null=True)),
                ('run_outs', models.IntegerField(blank=True, default=0, null=True)),
                ('match', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fielding', to='match.match')),
            ],
        ),
    ]
