from django.db import models
from django.contrib.auth.models import User
from .utilities import get_match
# Create your models here.
class Author(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="author")
    match = models.ManyToManyField('match.Match',related_name="author",blank=True)
    def __str__(self):
        return self.user.username
    
    
    @staticmethod
    def get_match_model():
        return get_match()