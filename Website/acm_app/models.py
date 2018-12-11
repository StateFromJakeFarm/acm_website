from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField

class ProblemModel(models.Model):
    '''
    Catalog problem info
    '''
    title       = models.CharField(max_length=100)
    slug        = models.SlugField(unique=True)
    description = MarkdownxField()
    author      = models.ForeignKey(User, on_delete=models.PROTECT)
    testcases   = models.FileField(upload_to='testcases', blank=True) # Expecting this to be a tarball of the .in and .out files
    time_limit  = models.FloatField(default=1) # Seconds to run testcase before declaring timeout

class LeaderboardModel(models.Model):
    '''
    Store a relationship between users and solved porblems
    '''
    # one to one USER
    # one to many ProblemModel
    # int score
