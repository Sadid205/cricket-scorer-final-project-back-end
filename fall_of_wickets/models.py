from django.db import models
from .utilities import get_batsman,get_match
# Create your models here.

class FallOfWickets(models.Model):
    batsman = models.OneToOneField('batsman.Batsman',related_name="batsman",null=True,blank=True,on_delete=models.CASCADE)
    score = models.IntegerField(null=True,blank=True,default=0)
    wicket = models.IntegerField(null=True,blank=True,default=0)
    match = models.ForeignKey('match.Match',null=True,blank=True,related_name='fall_of_wickets',on_delete=models.CASCADE)

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

