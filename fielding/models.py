from django.db import models
from .utilities import get_match
# Create your models here.

class Fielding(models.Model):
    catches = models.IntegerField(null=True,blank=True,default=0)
    stumpings = models.IntegerField(null=True,blank=True,default=0)
    run_outs = models.IntegerField(null=True,blank=True,default=0)
    match = models.ForeignKey('match.Match',related_name="fielding",null=True,blank=True,on_delete=models.CASCADE)

    def __str__(self):
        if self.match and self.match.team1 and self.match.team2:
            return f"{self.match.team1.team_name} vs {self.match.team2.team_name}"
        return "No Match Assigned"

    @staticmethod
    def get_match_model():
        return get_match()

