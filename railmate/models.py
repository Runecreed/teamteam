from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
    datetime = models.DateTimeField()       # ISO8601 formatted DateTime field
    datetime_end = models.DateTimeField()
    tripnumber = models.IntegerField()

    station_list = models.TextField(null=False, blank=False)

    # time = models.CharField(max_length=5)  # store hh:mm timestamp, parse later into DateTime object if need be
    # time_end = models.CharField(max_length=5)  # store hh:mm timestamp, parse later into DateTime object if need be

    deviation = models.IntegerField(blank=True,
                                    null=True)  # possible deviation, not required and stored as NULL if not given
    subscription = models.TextField()
    compensation = models.TextField()
    companions = models.IntegerField(verbose_name="Amount of Passengers coming with", default=0)
    max_companions = models.IntegerField(verbose_name="Total amount of extra passengers allowed",
                                         default=4)  # amount of people allowed with


class Search(models.Model):
    source = models.TextField()
    destination = models.TextField()
    date = models.DateField()
    time = models.CharField(max_length=5)  # store hh:mm timestamp, parse later into DateTime object if need be


    def space_left(self):
        if (self.companions >= self.max_companions):
            return False
        else:
            return True

    def __str__(self):  # verbose reporting of this entry
        # return str(self.user) + ' travels from ' + self.source + ' to ' + self.destination + ' on ' + \
        #        self.date.strftime('%d/%m/%y') + ' at ' + self.time + ' with ' + str(self.companions) + ' passengers'
        return str(self.user) + ' --- Tripnumber: ' + str(self.tripnumber) + ' starting station: '+ self.source + " endStation " + self.destination + ' || extra passengers: ' + str(
            self.companions)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatar", null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(default='-')


# AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Message(models.Model):
    content = models.TextField('Content', default='')
    sender = models.ForeignKey(User, related_name='sent_dm', verbose_name="Sender", default='',
                               on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_dm',
                                  verbose_name="Recipient", default='', on_delete=models.CASCADE)
    sent_at = models.DateTimeField("sent at", null=True, blank=True)
    read_at = models.DateTimeField("read at", null=True, blank=True)

    @property
    def unread(self):
        """returns whether the message was read or not"""
        if self.read_at is not None:
            return False
        return True

    def __str__(self):
        return self.content

    def save(self, **kwargs):
        if self.sender == self.recipient:
            raise ValidationError("You can't send messages to yourself")

        if not self.id:
            self.sent_at = datetime.datetime.now()
        super(Message, self).save(**kwargs)


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
