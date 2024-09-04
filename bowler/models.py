from django.db import models
from .utilities import get_match,get_player,get_team
# Create your models here.
class Bowler(models.Model):
    madien_over = models.IntegerField(null=True,blank=True)
    run = models.IntegerField(null=True,blank=True)
    wicket = models.IntegerField(null=True,blank=True)
    economy_rate = models.FloatField(null=True,blank=True)
    match = models.ForeignKey('match.Match',related_name="bowlers",null=True,blank=True,on_delete=models.CASCADE)
    player = models.ForeignKey('player.Player',related_name="bowler",null=True,blank=True,on_delete=models.CASCADE)
    team = models.ForeignKey('team.Team',on_delete=models.CASCADE,related_name="bowler",null=True,blank=True,)

    def __str__(self):
        if self.player and self.player.name:
            return self.player.name
        return "No Player Assigned In Team"

    @staticmethod
    def get_match_model():
        return get_match()
    
    @staticmethod
    def get_player_model():
        return get_player()
    
    @staticmethod
    def get_team_model():
        return get_team()
