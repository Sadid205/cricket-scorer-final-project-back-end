# Generated by Django 5.1.4 on 2024-12-15 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0004_alter_author_match_alter_author_user'),
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='team',
            field=models.ManyToManyField(blank=True, related_name='author', to='team.team'),
        ),
    ]
