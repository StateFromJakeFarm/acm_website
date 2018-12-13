from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from markdownx.models import MarkdownxField

class ProblemModel(models.Model):
    '''
    Catalog problem info
    '''
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = MarkdownxField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    testcases = models.FileField(upload_to='testcases', blank=True) # Expecting this to be a tarball of the .in and .out files
    time_limit = models.FloatField(default=1) # Seconds to run testcase before declaring timeout
    mem_limit = models.CharField(max_length=10, default='100m')
    memswap_limit = models.CharField(max_length=10, default='500m')

class LeaderboardModel(models.Model):
    '''
    Store a relationship between users and solved porblems
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(default=0)

    # one to many ProblemModel
    # int score
