from django.db import models
from .utilities import get_balls,get_bowler

class OverFI(models.Model):
    ball = models.ManyToManyField('balls.Balls',related_name='over_fi',blank=True)
    bowler = models.ForeignKey('bowler.Bowler',related_name='overs_fi',null=True,blank=True,on_delete=models.CASCADE)
    wide = models.IntegerField(default=0,null=True,blank=True)
    no_ball = models.IntegerField(default=0,null=True,blank=True)
    byes = models.IntegerField(default=0,null=True,blank=True)
    leg_byes = models.IntegerField(default=0,null=True,blank=True)
    wicket = models.IntegerField(default=0,null=True,blank=True)
    zero = models.IntegerField(default=0,null=True,blank=True)
    one = models.IntegerField(default=0,blank=True,null=True)
    two = models.IntegerField(default=0,null=True,blank=True)
    three = models.IntegerField(default=0,null=True,blank=True)
    four = models.IntegerField(default=0,null=True,blank=True)
    six = models.IntegerField(default=0,null=True,blank=True)
    palanty_runs = models.IntegerField(default=0,null=True,blank=True)
    scored_runs = models.IntegerField(default=0,null=True,blank=True)

    # def __str__(self):
    #     if self.match and self.match.team1 and self.match.team2:
    #         return f"{self.match.team1} vs {self.match.team2}"
    #     return "No Match Available"
 

    @staticmethod
    def get_balls_model():
        return get_balls()

    @staticmethod
    def get_bawler_model():
        return get_bowler()