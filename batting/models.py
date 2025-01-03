from django.db import models
from .utilities import get_team,get_player
# Create your models here.

class Batting(models.Model):
    player = models.ForeignKey("player.Player",related_name="batting",null=True,blank=True,on_delete=models.CASCADE)
    matches = models.ManyToManyField('match.Match',related_name="batting",blank=True)
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
    balls = models.IntegerField(default=0,null=True,blank=True)
    number_of_outs = models.IntegerField(default=0,null=True,blank=True)

    def __str__(self):
        if self.player and self.player.name:
            return self.player.name
        return "No Player Assigned"

    def save(self,*args,**kwargs):
        if self.runs > 0 and self.balls > 0:
            self.strike_rate = (self.runs/self.balls)*100
        if self.runs > 0 and self.number_of_outs > 0:
            self.average = self.runs/self.number_of_outs
        super().save(*args,**kwargs)

    @staticmethod
    def get_team_model():
        return get_team()

    @staticmethod
    def get_player_model():
        return get_player()

