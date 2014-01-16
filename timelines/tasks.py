import datetime

from celery import task

from django.db.models import Q, F
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
try:
    from django.utils.timezone import now
except ImportError:  # Django < 1.4
    now = datetime.datetime.now

from rapidsms.router import send

from .models import TimelineSubscription, Occurrence, Notification, Milestone

APPT_REMINDER = _('This is a reminder for your upcoming appointment on %(date)s. Please confirm.')


@task()
def generate_occurrences(days=14):
    """
    Task to create Occurrence instances based on current TimelineSubscriptions

    Arguments:
    days: The number of upcoming days to create Occurrences for
    """
    start = datetime.date.today()
    end = start + datetime.timedelta(days=days)

    subs = TimelineSubscription.objects.filter(Q(end__gte=now()) | Q(end__isnull=True))

    for sub in subs:
        for milestone in sub.timeline.milestones.all():
            milestone_date = sub.start.date() + datetime.timedelta(days=milestone.offset)
            #Create occurrence(s) for this subscription within the task window
            if start <= milestone_date <= end:
                appt, created = Occurrence.objects.get_or_create(
                                                    subscription=sub,
                                                    milestone=milestone,
                                                    date=milestone_date
                                                    )


@task()
def send_occurrence_notifications(days=7):
    """
    Task to send reminders notifications for upcoming Occurrence

    Arguments:
    days: The number of upcoming days to filter upcoming Occurrences
    """
    start = datetime.date.today()
    end = start + datetime.timedelta(days=days)
    blacklist = [Notification.STATUS_PENDING, Notification.STATUS_COMPLETED, Notification.STATUS_MANUAL]
    appts = Occurrence.objects.filter(
        # Join subscriptions that haven't ended
        Q(Q(subscription__connection__timelines__end__gte=now()) | Q(subscription__connection__timelines__end__isnull=True)),
        subscription__connection__timelines__timeline=F('milestone__timeline'),
        # Filter occurrences in range
        date__range=(start, end),
    ).exclude(actions__status__in=blacklist)
    for appt in appts:
        # TODO allow both static messages AND appointment reminders for a
        # milestone
        language = get_language()
        msg = None
        try:
            msg = appt.milestone.message
        except Milestone.DoesNotExist:
            pass
        if msg is not None:
            # if milestone has a default static message, fire away
            msg = appt.milestone.message
        else:
            # otherwise format message as an appointment reminder
            msg = APPT_REMINDER % {'date': appt.date}
        send(msg, appt.subscription.connection)
        Notification.objects.create(occurrence=appt,
                                    status=Notification.STATUS_PENDING,
                                    attempted=now(),
                                    message=msg)
