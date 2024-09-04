from django.db import models
from .utilities import get_fielder,get_match,get_team,get_bowler,get_player
from .constrains import HOWWICKETFALL
# Create your models here.

class Batsman(models.Model):
    player = models.ForeignKey('player.Player',on_delete=models.CASCADE,related_name="batsman",null=True,blank=True)
    run = models.IntegerField(default=0,null=True)
    ball = models.FloatField(default=0.0,null=True)
    four = models.IntegerField(default=0,null=True)
    six = models.IntegerField(default=0,null=True)
    strike_rate = models.FloatField(default=0.0,null=True)
    out_by = models.ForeignKey('bowler.Bowler',on_delete=models.CASCADE,null=True,blank=True)
    catch_by = models.ForeignKey('fielder.Fielder',on_delete=models.CASCADE,null=True,blank=True,related_name='catch_by_batsman')
    run_out_by = models.ForeignKey('fielder.Fielder',on_delete=models.CASCADE,null=True,blank=True,related_name='run_out_by_batsman')
    stumping_by = models.ForeignKey('fielder.Fielder',on_delete=models.CASCADE,null=True,blank=True,related_name='stumping_by_batsman')
    # over = models.ForeignKey('over.Over',on_delete=models.CASCADE,null=True,blank=True,related_name="batsman")
    match = models.ForeignKey('match.Match',on_delete=models.CASCADE,related_name='batsman',null=True,blank=True)
    is_out = models.BooleanField(default=False)
    how_wicket_fall = models.CharField(max_length=30,null=True,blank=True,choices=HOWWICKETFALL)
    team = models.ForeignKey('team.Team',on_delete=models.CASCADE,related_name="batsman",null=True,blank=True)
    
    # @staticmethod
    # def get_over_model():
    #     return get_over()

    def save(self,*args,**kwargs):
        if self.run > 0 and self.ball > 0:
            strikeRate = (self.run/self.ball)*100
            self.strike_rate = strikeRate
        super().save(*args,**kwargs)

    @staticmethod
    def get_match_model():
        return get_match()

    @staticmethod
    def get_fielder_model():
        return get_fielder()

    @staticmethod
    def get_team_model():
        return get_team()

    @staticmethod
    def get_bowler_model():
        return get_bowler()
    
    @staticmethod
    def get_player_model():
        return get_player()

    def __str__(self):
        if self.player and self.player.name:
            return self.player.name
        return "No Player Assigned In Team"