# Generated by Django 5.1.4 on 2024-12-22 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batting', '0005_batting_number_of_outs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batting',
            name='best_score',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
