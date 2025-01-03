from django.db import models
from .utilities import get_player,get_team
# Create your models here.

class Bowling(models.Model):
    player = models.ForeignKey('player.Player',related_name="bowling",on_delete=models.CASCADE,null=True,blank=True)
    team = models.ForeignKey('team.Team',related_name="bowling",on_delete=models.CASCADE,null=True,blank=True)
    matches = models.ManyToManyField('match.Match',related_name="bowling",blank=True)
    innings = models.IntegerField(null=True,blank=True,default=0)
    overs = models.FloatField(null=True,blank=True,default=0.0)
    madiens = models.IntegerField(null=True,blank=True,default=0)
    wickets = models.IntegerField(null=True,blank=True,default=0)
    runs = models.IntegerField(null=True,blank=True,default=0)
    best_bowling = models.CharField(max_length=30,null=True,blank=True,default="0/0")
    economy_rate = models.FloatField(null=True,blank=True,default=0.0)
    wides = models.IntegerField(null=True,blank=True,default=0)
    no_balls = models.IntegerField(null=True,blank=True,default=0)
    dot_balls = models.IntegerField(null=True,blank=True,default=0)
    tetra_wickets = models.IntegerField(null=True,blank=True,default=0)
    penta_wickets = models.IntegerField(null=True,blank=True,default=0)
    balls = models.IntegerField(default=0,null=True,blank=True)

    def __str__(self):
        if self.player and self.player.name:
            return self.player.name
        return "No Player Assigned"
    
    def save(self,*args,**kwargs):
        if self.overs>0 and self.runs>0:
            self.economy_rate = (self.runs/self.overs)
        super().save(*args,**kwargs)

    @staticmethod
    def get_team_model():
        return get_team()

    
    @staticmethod
    def get_player_model():
        return get_player()

