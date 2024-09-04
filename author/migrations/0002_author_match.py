# Generated by Django 5.1 on 2024-09-03 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0001_initial'),
        ('match', '0004_match_is_match_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='match',
            field=models.ManyToManyField(blank=True, null=True, related_name='account', to='match.match'),
        ),
    ]
