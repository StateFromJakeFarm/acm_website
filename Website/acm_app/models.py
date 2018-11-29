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
    testcases   = models.FileField(upload_to='testcases') # Expecting this to be a tarball of the .in and .out files
