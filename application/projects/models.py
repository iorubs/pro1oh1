from django.db import models
from authentication.models import Account

class Project(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=40, unique=False)
    p_type = models.CharField(max_length=40, unique=False, default='normal')
    clone_command = models.TextField(unique=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)

class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    folder = models.ForeignKey('self', blank=True, null=True ,on_delete=models.CASCADE)
    title = models.CharField(max_length=40, unique=False)
    f_type = models.CharField(max_length=10, unique=False)
    content = models.TextField(blank=True, null=True, default=' ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s" % (self.title)

    class Meta:
        ordering = ('title',)
