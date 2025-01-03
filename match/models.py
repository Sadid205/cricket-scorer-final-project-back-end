from django.db import models
from .constrains import ELECTED,INNINGS
from .utilities import get_team,get_batsman,get_bowler,get_fi_over,get_si_over
from bowling.models import Bowling
# Create your models here.

class Match(models.Model):
    team1 = models.ForeignKey('team.Team',related_name="host_team",on_delete=models.CASCADE,null=True,blank=True)
    team2 = models.ForeignKey('team.Team',related_name="visitor_team",on_delete=models.CASCADE,null=True,blank=True)
    total_over = models.IntegerField(default=5,null=True,blank=True)
    innings = models.CharField(max_length=20,choices=INNINGS,default="1st",null=True,blank=True)
    #First Innings
    first_innings_run_rate = models.FloatField(default=0.0,null=True,blank=True)
    first_innings_run = models.IntegerField(default=0,null=True,blank=True)
    first_innings_wicket = models.IntegerField(default=0,null=True,blank=True)
    first_innings_over = models.ManyToManyField('over_fi.OverFI',related_name='fi_match',blank=True)
    first_innings_nth_over = models.IntegerField(default=0,null=True,blank=True)
    first_innings_nth_ball = models.IntegerField(default=0,null=True,blank=True)

    #Second Innings
    second_innings_run_rate = models.FloatField(default=0.0,null=True,blank=True)
    second_innings_run = models.IntegerField(default=0,null=True,blank=True)
    second_innings_wicket = models.IntegerField(default=0,null=True,blank=True)
    second_innings_over = models.ManyToManyField('over_si.OverSI',related_name='si_match',blank=True)
    second_innings_nth_over = models.IntegerField(default=0,null=True,blank=True)
    second_innings_nth_ball = models.IntegerField(default=0,null=True,blank=True)

    is_match_finished = models.BooleanField(default=False,null=True,blank=True)
    match_status = models.CharField(max_length=100,null=True,blank=True,default="First innings running")
    nth_ball = models.IntegerField(default=0,null=True,blank=True)
    striker = models.ForeignKey('batsman.Batsman',related_name="curr_striker_batsman",on_delete=models.CASCADE,null=True,blank=True)
    non_striker = models.ForeignKey('batsman.Batsman',related_name="curr_non_striker_batsman",on_delete=models.CASCADE,null=True,blank=True)
    current_bowler = models.ForeignKey('bowler.Bowler',related_name="curr_bowler",on_delete=models.CASCADE,null=True,blank=True)
    toss_winner = models.ForeignKey('team.Team',related_name="toss_winner",on_delete=models.CASCADE,null=True,blank=True)
    elected = models.CharField(max_length=20,choices=ELECTED,default="Bat",null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.team1 and self.team2 and self.team1.team_name and self.team2.team_name:
            return f"{self.team1.team_name} vs {self.team2.team_name}"
        return "No Team Assigned"

    def save(self,*args,**kwargs):

        if self.innings=="1st" and (self.first_innings_nth_over==self.total_over or self.first_innings_wicket==10):
            self.match_status = "First innings finished"

        if (self.innings=="1st" and self.first_innings_nth_over==self.total_over-1) and self.nth_ball==6:
            self.first_innings_nth_over+=1
            self.first_innings_nth_ball=0
            self.nth_ball=0    

        if (self.innings=="2nd" and self.second_innings_nth_over==self.total_over-1) and self.nth_ball==6:
            self.second_innings_nth_over+=1    
            self.second_innings_nth_ball=0
            self.nth_ball=0 
        
        if self.innings=="2nd":
            if (self.toss_winner == self.team1 and self.elected=="Bat") or (self.toss_winner==self.team2 and self.elected=="Bowl"):
                self.match_status=f"{self.team2.team_name} team need {(self.first_innings_run+1)-self.second_innings_run} run to win"
                if (self.second_innings_run>self.first_innings_run) and (self.second_innings_nth_over<=self.total_over and self.second_innings_nth_ball>=0):
                    self.team2.won+=1
                    self.team2.save()
                    self.team1.lost+=1
                    self.team1.save()
                    self.match_status = f"{self.team2.team_name} team won by {10-self.second_innings_wicket} wicket"
                    self.is_match_finished=True
                elif (self.second_innings_run<self.first_innings_run) and (self.second_innings_nth_over==self.total_over and self.second_innings_nth_ball==0):
                    self.team1.won+=1
                    self.team1.save()
                    self.team2.lost+=1
                    self.team2.save()
                    self.is_match_finished=True
                    self.match_status = f"{self.team1.team_name} team won by {self.first_innings_run-self.second_innings_run} run"
                elif(self.second_innings_run==self.first_innings_run) and (self.second_innings_nth_over==self.total_over and self.second_innings_nth_ball==0):
                    self.match_status = "The match has been drawn."
                    self.is_match_finished=True
                else:
                    None
            else:
                self.match_status=f"{self.team1.team_name} team need {(self.first_innings_run+1)-self.second_innings_run} run to win"
                if (self.second_innings_run>self.first_innings_run) and (self.second_innings_nth_over<=self.total_over and self.second_innings_nth_ball>=0):
                    self.team1.won+=1
                    self.team1.save()
                    self.team2.lost+=1
                    self.team2.save()
                    self.match_status = f"{self.team1.team_name} team won by {10-self.second_innings_wicket} wicket"
                    self.is_match_finished=True
                elif (self.second_innings_run<self.first_innings_run) and (self.second_innings_nth_over==self.total_over and self.second_innings_nth_ball==0):
                    self.team2.won+=1
                    self.team2.save()
                    self.team1.lost+=1
                    self.team1.save()
                    self.match_status = f"{self.team2.team_name} team won by {self.first_innings_run-self.second_innings_run} run"
                    self.is_match_finished=True
                elif(self.second_innings_run==self.first_innings_run) and (self.second_innings_nth_over==self.total_over and self.second_innings_nth_ball==0):
                    self.match_status = "The match has been drawn."
                    self.is_match_finished=True
                else:
                    None
                    
        def count_maiden_overs(self):
            if self.innings=="1st":
                # self.first_innings_nth_over+=1
                overs = self.first_innings_over.all()
            else:
                # self.second_innings_nth_over+=1
                overs = self.second_innings_over.all()
            # self.nth_ball = 0
            existing_striker = self.striker
            self.striker = self.non_striker
            self.non_striker = existing_striker
            
            over=overs.last()
            if over is not None:
                bowling = Bowling.objects.filter(player__id=over.bowler.player.id).first()
                balls = over.ball.all()
                dot_balls = balls.filter(ball_types="DB")
                if len(balls)==6 and len(dot_balls)==6:
                    over.bowler.madien_over+=1
                    over.bowler.save()
                    if bowling is not None:
                        bowling.madiens+=1
                        bowling.save()

            

        if  self.nth_ball==6:
            count_maiden_overs(self=self)


        if self.innings=="1st" and self.first_innings_nth_over!=0 and self.first_innings_run!=0 and self.nth_ball!=0:
            self.first_innings_run_rate = self.first_innings_run/(self.first_innings_nth_over+(self.nth_ball/6))

        if self.innings=="2nd" and self.second_innings_nth_over!=0 and self.second_innings_run!=0 and self.nth_ball!=0:
            self.second_innings_run_rate = self.second_innings_run/(self.second_innings_nth_over+(self.nth_ball/6))

        super().save(*args,**kwargs)


    @staticmethod
    def get_team_model():
        return get_team()

    @staticmethod
    def get_bowler_model():
        return get_bowler()

    
    @staticmethod
    def get_batsman_model():
        return get_batsman()
    
    @staticmethod
    def get_fi_over_model():
        return get_fi_over()
    @staticmethod
    def get_si_over_model():
        return get_si_over()
