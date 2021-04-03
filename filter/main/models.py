from django.db import models

# Create your models here.
class Job(models.Model) :
    companyName = models.CharField(max_length=1000, default='Company Name')
    title = models.CharField(max_length=1000, default='Job Title')
    description = models.CharField(max_length=100000, default='Job Description')

    def __str__(self):
        display = str(self.companyName+ " ----> " +self.title)
        return display


class Application(models.Model):
    name = models.CharField(max_length=1000, default='Applicant Name')
    resume = models.FileField(upload_to="raw")

    def __str__(self):
        return self.name

class CSVfiles(models.Model):
    adID = models.IntegerField(default=0)
    csv = models.FileField(upload_to="converted")

    def __str__(self):
        return self.adID