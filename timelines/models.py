from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
try:
    from django.utils.timezone import now
except ImportError:  # Django < 1.4
    now = datetime.datetime.now


class Timeline(models.Model):
    "A series of milestones which users can subscribe for milestone events."

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, help_text=_('The keyword(s) to match '
        'in messages from the user. Specify multiple keywords by separating them '
        'with vertical bars. e.g., "birth|bith|bilth"'))

    def __unicode__(self):
        return self.name

    @property
    def keywords(self):
        return map(lambda k: k.strip().lower(), self.slug.split('|'))


class TimelineSubscription(models.Model):
    "Subscribing a user to a timeline of events."

    timeline = models.ForeignKey(Timeline, related_name='subscribers')
    connection = models.ForeignKey('rapidsms.Connection', related_name='timelines')
    pin = models.CharField(max_length=160, help_text=_('Name, phrase, or digits used when joining the timeline.'))
    start = models.DateTimeField(_('start date'), default=now)
    end = models.DateTimeField(_('end date'), default=None, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.connection, self.timeline)


class Milestone(models.Model):
    "A point on the timeline that when reached creates an occurrence."

    name = models.CharField(max_length=255)
    timeline = models.ForeignKey(Timeline, related_name='milestones')
    offset = models.IntegerField()

    # default message for simple timelines of non-interactive messages
    message = models.CharField(max_length=160, blank=True, null=True,
                               default=None)

    def __unicode__(self):
        return self.name


class Occurrence(models.Model):
    "Instance of a subscribed user hitting a milestone."

    STATUS_DEFAULT = 1
    STATUS_ACHIEVED = 2
    STATUS_MISSED = 3

    STATUS_CHOICES = [
        (STATUS_DEFAULT, _('Not Yet Occurred')),
        (STATUS_ACHIEVED, _('Achieved')),
        (STATUS_MISSED, _('Missed')),
    ]

    milestone = models.ForeignKey(Milestone, related_name='occurrences')
    subscription = models.ForeignKey(TimelineSubscription, related_name='occurrences')
    date = models.DateField(_('occurence date'))
    completed = models.DateTimeField(blank=True, null=True, default=None)
    reschedule = models.ForeignKey('self', blank=True, null=True,
                                   related_name='occurrences')
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_DEFAULT)
    notes = models.CharField(max_length=160, blank=True, default='')

    def __unicode__(self):
        return 'Occurrence for %s on %s' % (self.subscription.connection, self.date.isoformat())

    class Meta:
        ordering = ['-date']
        permissions = (
            ('view_occurrence', 'Can View Occurrences'),
        )


class Action(models.Model):

    STATUS_PENDING = 1
    STATUS_COMPLETED = 2
    STATUS_MANUAL = 3
    STATUS_ERROR = 4

    STATUS_CHOICES = (
        (STATUS_PENDING, _('Pending')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_MANUAL, _('Manually Confirmed')),
        (STATUS_ERROR, _('Error')),
    )

    occurrence = models.ForeignKey(Occurrence, related_name='actions')
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    attempted = models.DateTimeField(blank=True, null=True, default=now)
    completed = models.DateTimeField(blank=True, null=True, default=None)


class Notification(Action):
    "Record of subscriber notification for an action."

    message = models.CharField(max_length=160)

    def __unicode__(self):
        return 'Notification for %s on %s' %\
               (self.occurrence.subscription.connection,
                self.attempted.isoformat())

    def confirm(self, manual=False):
        "Mark occurrence as completed."
        completed = now()
        status = Notification.STATUS_MANUAL if manual else Notification.STATUS_COMPLETED
        self.completed = completed
        self.status = status
        Notification.objects.filter(pk=self.pk).update(completed=completed, status=status)
        self.occurrence.completed = completed
        Occurrence.objects.filter(pk=self.occurrence_id).update(completed=completed)
