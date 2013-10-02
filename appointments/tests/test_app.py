from __future__ import unicode_literals

import datetime

from .base import OccurrenceDataTestCase
from ..models import Occurrence, Notification
from ..tasks import generate_occurrences, send_occurrence_notifications


class OccurrenceAppTestCase(OccurrenceDataTestCase):
    "Integration test for larger SMS workflow."

    def setUp(self):
        super(OccurrenceAppTestCase, self).setUp()
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.milestone = self.create_milestone(timeline=self.timeline, offset=1)
        self.connection = self.lookup_connections('5555555555')[0]

    def test_join(self):
        "Join timeline then generate upcoming occurrences."
        msg = self.receive('APPT NEW FOO 123', self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        # Single occurrence should be created
        generate_occurrences()
        occurrence = Occurrence.objects.get(subscription__connection=self.connection, milestone=self.milestone)
        tomorrow = datetime.date.today() + datetime.timedelta(days=self.milestone.offset)
        self.assertEqual(tomorrow, occurrence.date)

    def test_confirm_occurrence(self):
        "Generate a notification and confirm an occurrence."
        subscription = self.create_timeline_subscription(connection=self.connection, timeline=self.timeline)
        generate_occurrences()
        send_occurrence_notifications()
        reminder = self.outbound.pop()
        self.assertTrue(reminder.text.startswith('This is a reminder'))
        msg = self.receive('APPT CONFIRM FOO {0}'.format(subscription.pin), self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        occurrence = Occurrence.objects.get(subscription__connection=self.connection, milestone=self.milestone)
        self.assertTrue(occurrence.completed)

    def test_made_occurrence(self):
        "Mark an occurrence as seen."
        yesterday = datetime.date.today() - datetime.timedelta(days=self.milestone.offset)
        # Joined yesterday so occurrence would be today
        subscription = self.create_timeline_subscription(
            connection=self.connection, timeline=self.timeline, start=yesterday)
        generate_occurrences()
        send_occurrence_notifications()
        reminder = self.outbound.pop()
        self.assertTrue(reminder.text.startswith('This is a reminder'))
        msg = self.receive('APPT STATUS FOO {0} ACHIEVED'.format(subscription.pin), self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        occurrence = Occurrence.objects.get(subscription__connection=self.connection, milestone=self.milestone)
        self.assertEqual(Occurrence.STATUS_ACHIEVED, occurrence.status)

    def test_missed_occurrence(self):
        "Mark an occurrence as missed."
        yesterday = datetime.date.today() - datetime.timedelta(days=self.milestone.offset)
        # Joined yesterday so occurrence would be today
        subscription = self.create_timeline_subscription(
            connection=self.connection, timeline=self.timeline, start=yesterday)
        generate_occurrences()
        send_occurrence_notifications()
        reminder = self.outbound.pop()
        self.assertTrue(reminder.text.startswith('This is a reminder'))
        msg = self.receive('APPT STATUS FOO {0} MISSED'.format(subscription.pin), self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        occurrence = Occurrence.objects.get(subscription__connection=self.connection, milestone=self.milestone)
        self.assertEqual(Occurrence.STATUS_MISSED, occurrence.status)

    def test_join_then_quit(self):
        "Join a timeline then quit."
        msg = self.receive('APPT NEW FOO 123', self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        msg = self.receive('APPT QUIT FOO 123', self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        generate_occurrences()
        # No occurrences should be generated
        occurrences = Occurrence.objects.filter(subscription__connection=self.connection)
        self.assertEqual(0, occurrences.count())

    def test_quit_reminders(self):
        "Don't send reminders for unsubscribed users."
        msg = self.receive('APPT NEW FOO 123', self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        generate_occurrences()
        msg = self.receive('APPT QUIT FOO 123', self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        send_occurrence_notifications()
        self.assertEqual(0, len(self.outbound), self.outbound)
        occurrence = Occurrence.objects.get(subscription__connection=self.connection, milestone=self.milestone)
        notifications = Notification.objects.filter(occurrence=occurrence)
        self.assertEqual(0, notifications.count())
