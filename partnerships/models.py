from django.db import models
from .utilities import get_batsman,get_match
# Create your models here.

class Partnerships(models.Model):
    batsman1 = models.ForeignKey('batsman.Batsman',related_name="batsman1",on_delete=models.CASCADE)
    batsman2 = models.ForeignKey('batsman.Batsman',related_name="batsman2",on_delete=models.CASCADE)
    total_run = models.IntegerField(null=True,blank=True,default=0)
    total_ball = models.FloatField(null=True,blank=True,default=0.0) 
    match = models.ForeignKey('match.Match',related_name="patnerships",on_delete=models.CASCADE)

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

