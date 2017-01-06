from django.db import models

class TutorialGroup(models.Model):
    title = models.CharField(max_length=50, unique=True)
    info = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('created_at',)


class Tutorial(models.Model):
    t_group = models.ForeignKey(TutorialGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('created_at',)
