from django.db import models
from .utilities import get_match
# Create your models here.

class Fielding(models.Model):
    player = models.ForeignKey("player.Player",related_name="fielding",null=True,blank=True,on_delete=models.CASCADE)
    catches = models.IntegerField(null=True,blank=True,default=0)
    stumpings = models.IntegerField(null=True,blank=True,default=0)
    run_outs = models.IntegerField(null=True,blank=True,default=0)
    matches = models.ManyToManyField('match.Match',related_name="fielding",blank=True)
    team = models.ForeignKey('team.Team',related_name="fielding",on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.player.name

    @staticmethod
    def get_match_model():
        return get_match()

