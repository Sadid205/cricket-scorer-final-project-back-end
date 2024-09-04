from django.db import models
# from .utilities import get_over
from .constrains import RUN,TYPES
# Create your models here.

class Balls(models.Model):
    ball_types = models.CharField(max_length=100,choices=TYPES,null=True,blank=True)
    runs = models.IntegerField(null=True,blank=True,choices=RUN,default=0)
    
    def __str__(self):
        return self.ball_types

    # @staticmethod
    # def get_over_model():
    #     return get_over()