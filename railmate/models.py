from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


# Create your models here.


class Trip(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Reference user table
    source = models.TextField()
    destination = models.TextField()
    date = models.DateField()
    time = models.CharField(max_length=5)  # store hh:mm timestamp, parse later into DateTime object if need be
    deviation = models.IntegerField(blank=True,
                                    null=True)  # possible deviation, not required and stored as NULL if not given
    subscription = models.TextField()
    compensation = models.TextField()
    companions = models.IntegerField(verbose_name="Amount of Passengers coming with", default=0)
    max_companions = models.IntegerField(verbose_name="Total amount of extra passengers allowed",
                                         default=4)  # amount of people allowed with

    def space_left(self):
        if (self.companions >= self.max_companions):
            return False
        else:
            return True

    def __str__(self):      # verbose reporting of this entry
        # return str(self.user) + ' travels from ' + self.source + ' to ' + self.destination + ' on ' + \
        #        self.date.strftime('%d/%m/%y') + ' at ' + self.time + ' with ' + str(self.companions) + ' passengers'
        return str(self.user) + ': ' + self.source + " --> " + self.destination + ' || passengers: ' + str(self.companions)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(default='-')



# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()