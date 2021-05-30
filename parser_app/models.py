from django.db import models
from django.contrib.postgres.fields import ArrayField
import os
from django.conf import settings
# Create your models here.

class RegisteredModel(models.Model):
    model_name = models.CharField(max_length=250, null=True, blank=True, unique=True)
    model_fields = ArrayField(models.CharField(max_length=250, null=True, blank=True, default=[]))
    mapped_fields = ArrayField(models.JSONField(null=True, blank=True, default=dict), null=True, blank =True)
    foreign_key_mapped_fields = ArrayField(models.JSONField(null=True, blank=True, default=dict), null=True, blank =True)    
    app_label_name = models.CharField(max_length=500)
    file_input = models.FileField(verbose_name='File Path', blank=True, null=True)
    def __str__(self):
        return str(self.model_name)

    def delete_file_input(self):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.file_input.name))
        self.file_input = None
        self.save()