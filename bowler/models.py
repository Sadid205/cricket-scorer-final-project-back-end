from django.db import models
from .utilities import get_match,get_player,get_team
from bowling.models import Bowling
# Create your models here.
class Bowler(models.Model):
    madien_over = models.IntegerField(null=True,blank=True,default=0)
    over = models.IntegerField(null=True,blank=True,default=0)
    nth_ball = models.IntegerField(null=True,blank=True,default=0)
    run = models.IntegerField(null=True,blank=True,default=0)
    wicket = models.IntegerField(null=True,blank=True,default=0)
    economy_rate = models.FloatField(null=True,blank=True,default=0.00)
    match = models.ForeignKey('match.Match',related_name="bowlers",null=True,blank=True,on_delete=models.CASCADE)
    player = models.ForeignKey('player.Player',related_name="bowler",null=True,blank=True,on_delete=models.CASCADE)
    team = models.ForeignKey('team.Team',on_delete=models.CASCADE,related_name="bowler",null=True,blank=True,)

    def save(self,*args,**kwargs):
        bowling = Bowling.objects.filter(player__id=self.player.id).first()
        
        if self.nth_ball==6:
            self.nth_ball=0
            self.over+=1
            if bowling is not None:
                bowling.overs+=1
                bowling.save()
        if bowling is not None:
            wickets = int(bowling.best_bowling.split('/')[0])
            runs = int(bowling.best_bowling.split('/')[1])
            if self.wicket==4:
                bowling.tetra_wickets+=1
            if self.wicket==5:
                bowling.penta_wickets+=1
            if self.wicket > wickets:
                bowling.best_bowling = f"{self.wicket}/{self.run}"
            if self.wicket==wickets:
                if self.run<runs:
                    bowling.best_bowling = f"{self.wicket}/{self.run}"
            bowling.save()
            
        if self.run>0:
            total_ball = self.over+(self.nth_ball/6)
            if total_ball>0:
                self.economy_rate = self.run/(total_ball)

        super().save(*args,**kwargs)


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
