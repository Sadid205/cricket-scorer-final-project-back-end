# Generated by Django 5.1.4 on 2024-12-28 15:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batsman', '0005_alter_batsman_how_wicket_fall'),
        ('match', '0005_match_first_innings_nth_ball_and_more'),
        ('partnerships', '0001_initial'),
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partnerships',
            name='batsman1',
        ),
        migrations.RemoveField(
            model_name='partnerships',
            name='batsman2',
        ),
        migrations.AddField(
            model_name='partnerships',
            name='extras',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='partnerships',
            name='non_striker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='non_striker_patnerships', to='batsman.batsman'),
        ),
        migrations.AddField(
            model_name='partnerships',
            name='striker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='striker_patnerships', to='batsman.batsman'),
        ),
        migrations.AddField(
            model_name='partnerships',
            name='team',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='patnarships', to='team.team'),
        ),
        migrations.AlterField(
            model_name='partnerships',
            name='match',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='patnerships', to='match.match'),
        ),
        migrations.AlterField(
            model_name='partnerships',
            name='total_ball',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
