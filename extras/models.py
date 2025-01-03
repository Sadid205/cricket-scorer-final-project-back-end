from django.db import models
from .utilities import get_match
# Create your models here.

class Extras(models.Model):
    byes = models.IntegerField(null=True,blank=True,default=0)
    leg_byes = models.IntegerField(null=True,blank=True,default=0)
    wide = models.IntegerField(null=True,blank=True,default=0)
    no_ball = models.IntegerField(null=True,blank=True,default=0)
    panalty = models.IntegerField(null=True,blank=True,default=0)
    match = models.ForeignKey('match.Match',related_name="extras",null=True,blank=True,on_delete=models.CASCADE) 
    team = models.ForeignKey('team.Team',related_name="extras",null=True,blank=True,on_delete=models.CASCADE,default=1)

    def __str__(self):
        if self.match and self.match.team1 and self.match.team2:
            return f"{self.match.team1.team_name} vs {self.match.team2.team_name}"
        return "No Match Assigned"
        
    @staticmethod
    def get_match_model():
        return get_match()

