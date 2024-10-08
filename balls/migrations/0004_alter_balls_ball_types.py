# Generated by Django 5.1 on 2024-09-08 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('balls', '0003_alter_balls_ball_types_alter_balls_runs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balls',
            name='ball_types',
            field=models.CharField(blank=True, choices=[('WD', 'WD'), ('NB', 'NB'), ('BYE', 'BYE'), ('LB', 'LB'), ('DB', 'DB'), ('One', 'One'), ('Two', 'Two'), ('Three', 'Three'), ('Four', 'FOUR'), ('Five', 'Five'), ('Six', 'SIX'), ('CO', 'CO'), ('RO', 'RO'), ('LBW', 'LBW'), ('HTB', 'HTB'), ('OTF', 'OTF'), ('OT', 'OT'), ('BO', 'BO'), ('S', 'S'), ('HW ', 'HW'), ('WD&RO', 'WD&RO'), ('WD&S', 'WD&S'), ('WD&HW', 'WD&HW'), ('NO&RO', 'NO&RO'), ('NO&B', 'NO&B'), ('NO&CO', 'NO&CO'), ('NO&S', 'NO&S'), ('NO&LBW', 'NO&LBW'), ('NO&HW', 'NO&HW'), ('BYE&RO', 'BYE&RO'), ('LGB&RO', 'LGB&RO'), ('LGB&S', 'LGB&S'), ('BYE&S', 'BYE&S'), ('BYE&HW', 'BYE&HW'), ('LGB&HW', 'LGB&HW'), ('NO&BYE', 'NO&BYE'), ('NO&LB', 'NO&LB')], max_length=100, null=True),
        ),
    ]
