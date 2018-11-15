from django.db import models
from django.contrib.auth.models import User

class ProblemModel(models.Model):
    '''
    Catalog problem info
    '''
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
