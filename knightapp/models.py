from django.db import models

def file_destination(instance, filename):
    return 'user_uploads/' + instance.generated_id + '.csv'

class Uploaded_File(models.Model):
    generated_id = models.CharField(max_length=25)
    uploaded_file = models.FileField(upload_to=file_destination)
    def __unicode__(self):
        return self.generated_id
