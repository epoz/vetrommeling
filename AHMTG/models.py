from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import json

class EmailOrUsernameModelBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
 
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
            
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    school = models.ForeignKey('School', related_name='users', blank=True, null=True)
    pybossa_server = models.CharField(max_length=250, blank=True, null=True)
    pybossa_api_key = models.CharField(max_length=250, blank=True, null=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class School(models.Model):
    class Meta:
        verbose_name_plural = 'Scholen'

    name = models.CharField(max_length=250)
    def __unicode__(self):
        return self.name

class App(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
# Soon we need to add the App to Vraag as a ForeignKey
# Also, make the app multi-lingual.
# Rename the App to vetrommelingh
# Make the sources of objects selectable, right now AdLib searches as default
# but you could also for example do RSS Mediafeeds or some other things that 
# produces objects to work on.

class Vraag(models.Model):
    class Meta:
        verbose_name_plural = 'Vragen'

    txt = models.TextField()
    uitleg = models.TextField(blank=True)

    def __unicode__(self):
        return self.txt

class Keuze(models.Model):
    class Meta:
        verbose_name_plural = 'Keuzes'

    optie = models.TextField()
    data = models.CharField(max_length=200, blank=True)
    vraag = models.ForeignKey('Vraag', related_name='opties')
    vrij = models.BooleanField(default=False)

class Serie(models.Model):
    naam = models.CharField(max_length=250)
    adlibsearch = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.naam

class SerieVraag(models.Model):
    serie = models.ForeignKey('Serie', related_name='vragen')
    vraag = models.ForeignKey('Vraag', related_name='series')
    def __unicode__(self):
        return u'%s - %s' % (self.serie, self.vraag)

class SerieItem(models.Model):
    serie = models.ForeignKey('Serie', related_name='items')
    objid = models.CharField(max_length=250)
    objdata = models.TextField()
    def __unicode__(self):
        return u'%s - %s' % (self.serie, self.objid)
    @property
    def obj(self):
        return json.loads(self.objdata)

class Antwoord(models.Model):
    class Meta:
        verbose_name_plural = 'Antwoorden'

    serievraag = models.ForeignKey('SerieVraag', related_name='antwoorden')
    user = models.ForeignKey(User, related_name='antwoorden')
    obj = models.CharField(max_length=250)
    value = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    exported = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'%s - %s %s' % (self.user.email, self.serievraag.vraag.txt, self.value)