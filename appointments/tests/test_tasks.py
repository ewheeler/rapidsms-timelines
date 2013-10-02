from __future__ import unicode_literals

import datetime

from .base import OccurrenceDataTestCase, Occurrence, Milestone, Notification, now
from ..tasks import generate_occurrences, send_occurrence_notifications, APPT_REMINDER


class GenerateOccurrencesTestCase(OccurrenceDataTestCase):
    "Task to generate future occurrences"

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.offsets = [1, 3, 7, 14, 30]
        for offset in self.offsets:
            self.create_milestone(name='{0} day(s)'.format(offset), offset=offset, timeline=self.timeline)
        self.sub = self.create_timeline_subscription(timeline=self.timeline)
        self.cnx = self.sub.connection

    def test_generate_occurrences(self):
        "Test the default task"
        self.assertEqual(0, Occurrence.objects.filter(subscription__connection=self.cnx).count())
        generate_occurrences()
        self.assertEqual(4, Occurrence.objects.filter(subscription__connection=self.cnx).count())

    def test_generate_occurrences_already_exists(self):
        "The task should generate no occurrences if the series already exists for the user"
        self.cnx = self.sub.connection
        for offset in self.offsets:
            date = now() + datetime.timedelta(days=offset)
            milestone = Milestone.objects.get(offset=offset)
            self.create_occurrence(subscription=self.sub, date=date, milestone=milestone)
        self.assertEqual(5, Occurrence.objects.filter(subscription__connection=self.cnx).count())
        generate_occurrences()
        self.assertEqual(5, Occurrence.objects.filter(subscription__connection=self.cnx).count())

    def test_generate_occurrences_out_of_range(self):
        "The task should generate no occurrences if the milestones are out of range"
        Milestone.objects.all().delete()
        offsets = [15, 17]
        for offset in offsets:
            self.create_milestone(name='{0} day(s)'.format(offset), offset=offset, timeline=self.timeline)
        self.assertEqual(0, Occurrence.objects.filter(subscription__connection=self.cnx).count())
        generate_occurrences()
        self.assertEqual(0, Occurrence.objects.filter(subscription__connection=self.cnx).count())

    def test_generate_occurrences_multiple_subscriptions(self):
        "The task should generate occurrences for all applicable subscriptions"
        self.assertEqual(0, Occurrence.objects.all().count())
        self.create_timeline_subscription(timeline=self.timeline)
        generate_occurrences()
        self.assertEqual(8, Occurrence.objects.all().count())

    def test_generate_occurrences_for_n_days(self):
        "The task should generate occurrences when supplied N days as an argument"
        self.assertEqual(0, Occurrence.objects.all().count())
        generate_occurrences(30)
        self.assertEqual(5, Occurrence.objects.all().count())


class SendOccurrenceNotificationsTestCase(OccurrenceDataTestCase):
    "Task to send notifications for upcoming Occurrences"

    def setUp(self):
        self.backend = self.create_backend(name='mockbackend')
        self.cnx = self.create_connection(backend=self.backend)
        self.timeline = self.create_timeline()
        self.subscription = self.create_timeline_subscription(connection=self.cnx, timeline=self.timeline)
        self.occurrence = self.create_occurrence(subscription=self.subscription)

    def create_milestone(self, **kwargs):
        "Ensure milestones are created on the default timeline."
        kwargs['timeline'] = self.timeline
        return super(SendOccurrenceNotificationsTestCase, self).create_milestone(**kwargs)

    def test_send_notifications(self):
        "Test the default task"
        self.assertEqual(0, Notification.objects.filter(occurrence=self.occurrence).count())
        send_occurrence_notifications()
        self.assertEqual(1, Notification.objects.filter(occurrence=self.occurrence).count())
        msg = APPT_REMINDER % {'date': self.occurrence.date}
        self.assertEqual(self.outbound[0].text, msg)
        self.assertEqual(self.outbound[0].connection, self.cnx)

    def test_send_notifications_not_notified(self):
        "The task should generate no notifications if a reminder has already been sent"
        self.create_notification(occurrence=self.occurrence, status=1)
        self.assertEqual(1, Notification.objects.filter(occurrence=self.occurrence).count())
        send_occurrence_notifications()
        self.assertEqual(1, Notification.objects.filter(occurrence=self.occurrence).count())
        self.assertEqual(0, len(self.outbound))

    def test_send_notifications_out_of_range(self):
        "The task should generate no notifications if the occurrence(s) are out of range"
        self.occurrence.date = self.occurrence.date + datetime.timedelta(days=10)
        self.occurrence.save()
        self.assertEqual(0, Notification.objects.filter(occurrence=self.occurrence).count())
        send_occurrence_notifications()
        self.assertEqual(0, Notification.objects.filter(occurrence=self.occurrence).count())
        self.assertEqual(0, len(self.outbound))

    def test_send_notifications_multiple_users(self):
        "The task should generate notifications for all applicable occurrences"
        self.cnx2 = self.create_connection(identity='johndoe', backend=self.backend)
        self.sub2 = self.create_timeline_subscription(connection=self.cnx2, timeline=self.timeline)
        self.create_occurrence(subscription=self.sub2)
        self.assertEqual(0, Notification.objects.all().count())
        send_occurrence_notifications()
        self.assertEqual(2, Notification.objects.all().count())
        self.assertEqual(2, len(self.outbound))

    def test_send_notifications_for_n_days(self):
        "The task should generate occurrences when supplied N days as an argument"
        self.create_occurrence(subscription=self.subscription, date=now() + datetime.timedelta(days=10))
        self.assertEqual(0, Notification.objects.all().count())
        send_occurrence_notifications(30)
        self.assertEqual(2, Notification.objects.all().count())
        self.assertEqual(2, len(self.outbound))
