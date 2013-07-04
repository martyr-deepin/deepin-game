from django.db import models
from tagging.fields import TagField

class App(models.Model): 
    appid = models.IntegerField(primary_key=True, )
    name = models.CharField(max_length=255)
    tags = TagField()
    
    def __unicode__(self):
        return self.name

