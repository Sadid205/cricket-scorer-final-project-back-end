from django.db import models

# Create your models here.

class Team(models.Model):
    team_name = models.CharField(max_length=100,null=True,blank=True)
    matches = models.IntegerField(null=True,blank=True,default=0)
    won = models.IntegerField(null=True,blank=True,default=0)
    lost = models.IntegerField(null=True,blank=True,default=0)

    def __str__(self):
        return self.team_name