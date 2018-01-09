from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
import datetime


# Create your models here.

class Trips(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Reference user table
    source = models.TextField()
    destination = models.TextField()
    date = models.DateField()
    time = models.CharField(max_length=4)  # store hh:mm timestamp, parse later into DateTime object if need be
    deviation = models.IntegerField(blank=True,
                                    null=True)  # possible deviation, not required and stored as NULL if not given
    subscription = models.TextField()
    compensation = models.TextField()
    companions = models.IntegerField(verbose_name="Amount of Passengers coming with", default=0)
    max_companions = models.IntegerField(verbose_name="Total amount of extra passengers allowed",
                                         default=4)  # amount of people allowed with

    def spaceLeft(self):
        if (self.companions >= self.max_companions):
            return False
        else:
            return True

    def __str__(self):      #verbose reporting of this entry
        return self.user + ' travels from ' + self.source + ' to ' + self.destination + ' on ' + \
               self.date.strftime('%d/%m/%y') + ' at ' + self.time + ' with ' + str(self.companions) + ' passengers'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatar/')
    birth_date = models.DateField()
