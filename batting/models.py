from django.db import models
from .utilities import get_team,get_player
# Create your models here.

class Batting(models.Model):
    player = models.ForeignKey("player.Player",related_name="batting",null=True,blank=True,on_delete=models.CASCADE)
    matches = models.IntegerField(default=0,null=True,blank=True)
    innings = models.IntegerField(default=0,null=True,blank=True)
    runs = models.IntegerField(default=0,null=True,blank=True)
    not_outs = models.IntegerField(default=0,null=True,blank=True)
    best_score = models.IntegerField(default=0,null=True,blank=True)
    strike_rate = models.FloatField(default=0.0,null=True,blank=True)
    average = models.FloatField(default=0.0,null=True,blank=True)
    fours = models.IntegerField(default=0,null=True,blank=True)
    sixs = models.IntegerField(default=0,null=True,blank=True)
    thirties = models.IntegerField(default=0,null=True,blank=True)
    fifties = models.IntegerField(default=0,null=True,blank=True)
    hundreds = models.IntegerField(default=0,null=True,blank=True)
    duckes = models.IntegerField(default=0,null=True,blank=True)
    team = models.ForeignKey('team.Team',related_name="batting",null=True,blank=True,on_delete=models.CASCADE)

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

