# Generated by Django 5.1.4 on 2024-12-22 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bowling', '0004_alter_bowling_best_bowling'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bowling',
            name='best_bowling',
            field=models.CharField(blank=True, default='0/0', max_length=30, null=True),
        ),
    ]
