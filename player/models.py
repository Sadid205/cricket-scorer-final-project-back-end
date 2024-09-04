from django.db import models
from .utilities import get_team
# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=50,null=True)
    image = models.ImageField(upload_to='images/',blank=True)
    team = models.ForeignKey('team.Team',related_name="players",null=True,blank=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @staticmethod
    def get_team_model():
        return get_team()
