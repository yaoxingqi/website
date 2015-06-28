from datetime import datetime, timedelta
from django.db import models

from sponsors.models import Sponsor
from wagtail.wagtailsnippets.models import register_snippet

import logging
from pytz import UTC

log = logging.getLogger('meetups')


class MeetupUpdate(models.Model):
    """ Poor man's caching for meetups
    """
    updated = models.DateTimeField(auto_now_add=True)

    @classmethod
    def tick(cls):
        """ Record Datetime of latest Meetup update
       """
        meetup_update = cls.objects.filter().first()
        now = datetime.now(tz=UTC)
        if not meetup_update:
            meetup_update = cls()
        meetup_update.updated = now
        meetup_update.save()

    @classmethod
    def _invalidate_meetup_update(cls):
        """ Invalidate the MeetupUpdate by making more than an hour ago
        """
        meetup_update = cls.objects.filter().get()
        meetup_update.updated = datetime.now(tz=UTC) - timedelta(hours=1)
        meetup_update.save(force_update=True, update_fields=['updated'])


class MeetupSponsorRelationship(models.Model):
    """ Qualify how sponsor helped what meetup
    Pivot table for Sponsor M<-->M Meetup
    """
    sponsor = models.ForeignKey(Sponsor)
    meetup = models.ForeignKey('Meetup')
    note = models.TextField(blank=True, default='')


@register_snippet
class Meetup(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    name = models.CharField(max_length=255, blank=False)
    description = models.TextField()
    event_url = models.URLField()

    sponsors = models.ManyToManyField(Sponsor, through=MeetupSponsorRelationship, null=True, blank=True)

    time = models.DateTimeField()
    created = models.DateTimeField()
    updated = models.DateTimeField()

    rsvps = models.IntegerField(default=0)
    maybe_rsvps = models.IntegerField(default=0)
    waitlist_count = models.IntegerField(default=0)

    status = models.CharField(max_length=255, blank=False)
    visibility = models.CharField(max_length=255, blank=False)

    class Meta:
        ordering = ['time']

    def __str__(self):
        return self.name

    @classmethod
    def future_events(cls):
        today = datetime.now()
        return cls.objects.filter(time__gt=today)

