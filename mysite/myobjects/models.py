from django.db import models


class MyObject(models.Model):
    form_field = models.FileField(upload_to=u'dummy')
