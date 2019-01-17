from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from markdownx.models import MarkdownxField

class LeaderboardModel(models.Model):
    '''
    Store a relationship between users and solved porblems
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(default=0)

class UserSolvedProblems(models.Model):
    '''
    Keep track of which problems each user has solved
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    problem = models.ForeignKey('ProblemModel', on_delete=models.CASCADE, null=False)

class ParticipantModel(models.Model):
    '''
    Track a participant's score within a competition.
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    solved = models.IntegerField(default=0)
    penalty = models.IntegerField(default=0) # Seconds

class ContestModel(models.Model):
    '''
    Facilitate an ICPC-style programming competition.
    '''
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(ParticipantModel)

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
    contest = models.ForeignKey(ContestModel, on_delete=models.PROTECT, null=True) # FK to contest (NULL if not part of contest)

class SubmissionModel(models.Model):
    '''
    Record problem submissions
    '''
    problem = models.ForeignKey(ProblemModel, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    submission_file = models.FileField(upload_to='submissions', blank=False)
    correct = models.BooleanField(default=False)
    submission_time = models.DateTimeField(null=True)
