# Generated by Django 5.1.4 on 2024-12-13 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('over_si', '0002_alter_oversi_ball'),
    ]

    operations = [
        migrations.AddField(
            model_name='oversi',
            name='legal_ball_numbers',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
