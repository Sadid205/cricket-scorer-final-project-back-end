# Generated by Django 5.1.4 on 2024-12-22 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batting', '0004_alter_batting_best_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='batting',
            name='number_of_outs',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
