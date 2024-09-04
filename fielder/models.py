from django.db import models
from .utilities import get_team,get_player
# Create your models here.
class Fielder(models.Model):
    team = models.ForeignKey('team.Team',related_name="fielder",null=True,blank=True,on_delete=models.CASCADE)
    matches = models.IntegerField(null=True,blank=True,default=0)
    catches = models.IntegerField(null=True,blank=True,default=0)
    stumpings = models.IntegerField(null=True,blank=True,default=0)
    run_outs = models.IntegerField(null=True,blank=True,default=0)
    player = models.ForeignKey('player.Player',null=True,blank=True,related_name="fielder",on_delete=models.CASCADE)

    def __str__(self):
        if self.player and self.player.name:
            return self.player.name
        return "No Player Assigned"        

    @staticmethod
    def get_team_model():
        return get_team()
    
    @staticmethod
    def get_player_model():
        return get_player()
    
