from django.db import models
from .utilities import get_batsman,get_match
# Create your models here.

class Partnerships(models.Model):
    striker = models.ForeignKey('batsman.Batsman',related_name="striker_patnerships",on_delete=models.CASCADE,default=1)
    non_striker = models.ForeignKey('batsman.Batsman',related_name="non_striker_patnerships",on_delete=models.CASCADE,default=1)
    striker_runs = models.IntegerField(null=True,blank=True,default=0)
    non_striker_runs = models.IntegerField(null=True,blank=True,default=0)
    total_run = models.IntegerField(null=True,blank=True,default=0)
    total_ball = models.IntegerField(null=True,blank=True,default=0) 
    match = models.ForeignKey('match.Match',related_name="patnerships",on_delete=models.CASCADE,default=1)
    extras = models.IntegerField(null=True,blank=True,default=0)
    team = models.ForeignKey('team.Team',related_name='patnarships',on_delete=models.CASCADE,default=1)

    def __str__(self):
        if self.match and self.match.team1 and self.match.team2:
            return f"{self.match.team1.team_name} vs {self.match.team2.team_name}"
        return "No Match Assigned"
            
    @staticmethod
    def get_match_model():
        return get_match()

 
    @staticmethod
    def get_batsman_model():
        return get_batsman()

