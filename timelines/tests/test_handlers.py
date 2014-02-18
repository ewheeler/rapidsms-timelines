from __future__ import unicode_literals

from datetime import timedelta

from .base import (OccurrenceDataTestCase, Notification, Occurrence,
    TimelineSubscription, now)
from ..handlers.base import AppointmentHandler
from ..handlers.confirm import ConfirmHandler
from ..handlers.move import MoveHandler
from ..handlers.new import NewHandler
from ..handlers.quit import QuitHandler
from ..handlers.status import StatusHandler
from ..handlers.subscribe import SubscribeHandler


class NewHandlerTestCase(OccurrenceDataTestCase):
    "Keyword handler for adding users to timelines"

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.prefix = AppointmentHandler.prefix

    def test_help(self):
        "Prefix and keyword should return the help for adding subscriptions."
        replies = NewHandler.test('APPT NEW')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(self.prefix + ' NEW <KEY> <NAME/ID> <DATE>' in reply)

    def test_match(self):
        "Send a successful match to create user timeline subscription."
        replies = NewHandler.test('APPT NEW foo bar')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_match_with_date(self):
        "Use start date if given."
        tomorrow = (now() + timedelta(days=1)).strftime('%Y-%m-%d')
        replies = NewHandler.test('APPT NEW foo bar %s' % tomorrow)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_no_keyword_match(self):
        "Keyword does not match any existing timelines."
        self.timeline.delete()
        replies = NewHandler.test('APPT NEW foo bar')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_no_name_given(self):
        "No name is given."
        replies = NewHandler.test('APPT NEW foo')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_invalid_date_format_given(self):
        "Invalid date format."
        replies = NewHandler.test('APPT NEW foo bar baz')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_already_joined(self):
        "Attempting to register and already registered connection/name pair."
        connection = self.create_connection()
        NewHandler._mock_backend = connection.backend
        self.create_timeline_subscription(timeline=self.timeline,
            connection=connection, pin='bar')
        replies = NewHandler.test('APPT NEW foo bar', identity=connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))
        del NewHandler._mock_backend


class ConfirmHandlerTestCase(OccurrenceDataTestCase):
    "Keyword handler for confirming occurrences."

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.connection = self.create_connection()
        self.subscription = self.create_timeline_subscription(
            timeline=self.timeline, connection=self.connection, pin='bar')
        ConfirmHandler._mock_backend = self.connection.backend
        self.milestone = self.create_milestone(timeline=self.timeline)
        self.occurrence = self.create_occurrence(milestone=self.milestone)
        self.notification = self.create_notification(occurrence=self.occurrence)
        self.prefix = AppointmentHandler.prefix

    def test_help(self):
        "Prefix and keyword should return the help."
        replies = ConfirmHandler.test('APPT CONFIRM')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(self.prefix + ' CONFIRM <KEY> <NAME/ID>' in reply)

    def test_occurrence_confirmed(self):
        "Successfully confirm an upcoming occurrence."
        replies = ConfirmHandler.test('APPT CONFIRM foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'))
        notification = Notification.objects.get(pk=self.notification.pk)
        self.assertTrue(notification.completed)
        self.assertEqual(notification.status, Notification.STATUS_COMPLETED)
        occurrence = Occurrence.objects.get(pk=self.occurrence.pk)
        self.assertTrue(occurrence.completed)

    def test_no_upcoming_occurrence(self):
        "Matched user has no upcoming occurrence notifications."
        self.notification.delete()
        replies = ConfirmHandler.test('APPT CONFIRM foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no uncompleted' in reply)

    def test_already_confirmed(self):
        "Matched user has already confirmed the upcoming occurrence."
        self.notification.confirm()
        replies = ConfirmHandler.test('APPT CONFIRM foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no uncompleted' in reply)

    def test_no_subscription(self):
        "Name/ID does not match a subscription."
        self.subscription.delete()
        replies = ConfirmHandler.test('APPT CONFIRM foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('does not match an active subscription' in reply)

    def test_subscription_ended(self):
        "Name/ID subscription has ended."
        self.subscription.end = now()
        self.subscription.save()
        replies = ConfirmHandler.test('APPT CONFIRM foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('does not match an active subscription' in reply)


class StatusHandlerTestCase(OccurrenceDataTestCase):
    "Keyword handler for updating the status of occurrences."

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.connection = self.create_connection()
        self.subscription = self.create_timeline_subscription(
            timeline=self.timeline, connection=self.connection, pin='bar')
        StatusHandler._mock_backend = self.connection.backend
        self.milestone = self.create_milestone(timeline=self.timeline)
        self.occurrence = self.create_occurrence(milestone=self.milestone)
        self.prefix = AppointmentHandler.prefix

    def test_help(self):
        "Prefix and keyword should return the help."
        replies = StatusHandler.test('APPT STATUS')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(self.prefix + ' STATUS <KEY> <NAME/ID> <SAW|MISSED>' in reply)

    def test_occurrence_status_updated(self):
        "Successfully update a recent occurrence."
        for status in Occurrence.STATUS_CHOICES[1:]:
            appt = self.create_occurrence(milestone=self.milestone)
            replies = StatusHandler.test('APPT STATUS foo bar %s' % status[1].upper(),
                                         identity=self.connection.identity)
            self.assertEqual(len(replies), 1)
            reply = replies[0]
            self.assertTrue(reply.startswith('Thank you'))
            self.assertTrue(appt.status, status[0])

    def test_occurrence_status_invalid_update(self):
        "Do not update if supplied status text is not in STATUS_CHOICES."
        replies = StatusHandler.test('APPT STATUS foo bar FOO', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry, the status update must be in'))

    def test_no_recent_occurrence(self):
        "Matched user has no recent occurrence."
        self.occurrence.delete()
        replies = StatusHandler.test('APPT STATUS foo bar SAW', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no recent occurrences' in reply)

    def test_no_recent_occurrence_needing_update(self):
        "Matched user has no recent occurrence that needs updating."
        self.occurrence.status = Occurrence.STATUS_MISSED
        self.occurrence.save()
        replies = StatusHandler.test('APPT STATUS foo bar MISSED', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no recent occurrences' in reply)

    def test_future_occurrence(self):
        "Matched user has no recent occurrence."
        self.occurrence.date = self.occurrence.date + timedelta(days=1)
        self.occurrence.save()
        replies = StatusHandler.test('APPT STATUS foo bar SAW', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no recent occurrences' in reply)

    def test_no_subscription(self):
        "Name/ID does not match a subscription."
        self.subscription.delete()
        replies = StatusHandler.test('APPT STATUS foo bar SAW', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('does not match an active subscription' in reply)

    def test_subscription_ended(self):
        "Name/ID subscription has ended."
        self.subscription.end = now()
        self.subscription.save()
        replies = StatusHandler.test('APPT STATUS foo bar MISSED', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('does not match an active subscription' in reply)


class MoveHandlerTestCase(OccurrenceDataTestCase):
    "Keyword handler for rescheduling of occurrences."

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.connection = self.create_connection()
        self.subscription = self.create_timeline_subscription(
            timeline=self.timeline, connection=self.connection, pin='bar')
        MoveHandler._mock_backend = self.connection.backend
        self.milestone = self.create_milestone(timeline=self.timeline)
        self.occurrence = self.create_occurrence(milestone=self.milestone,
                                                   date=now() + timedelta(hours=1))
        self.tomorrow = (now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.prefix = AppointmentHandler.prefix

    def test_help(self):
        "Prefix and keyword should return the help."
        replies = MoveHandler.test('APPT MOVE')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(self.prefix + ' MOVE <KEY> <NAME/ID> <DATE>' in reply)

    def test_occurrence_reschedule(self):
        "Successfully reschedule an upcoming occurrence."
        self.assertEqual(1, Occurrence.objects.all().count())
        replies = MoveHandler.test('APPT MOVE foo bar %s' % self.tomorrow,
                                   identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'))
        self.assertEqual(2, Occurrence.objects.all().count())
        reschedule = Occurrence.objects.all()[0]
        self.assertEqual(reschedule.occurrences.all()[0], self.occurrence)

    def test_occurrence_reschedule_malformed_date(self):
        "Ensure the date is properly formatted."
        replies = MoveHandler.test('APPT MOVE foo bar tomorrow',
                                   identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry, we cannot understand that date format'))

    def test_occurrence_reschedule_future_date(self):
        "Ensure the date must be in the future."
        yesterday = (now() - timedelta(days=1)).strftime('%Y-%m-%d')
        replies = MoveHandler.test('APPT MOVE foo bar %s' % yesterday,
                                   identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry, the reschedule date'))

    def test_no_future_occurrence(self):
        "Matched user has no future occurrence."
        self.occurrence.delete()
        replies = MoveHandler.test('APPT MOVE foo bar %s' % self.tomorrow,
                                     identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no future occurrences' in reply)

    def test_no_future_occurrence_needing_update(self):
        "Matched user has no future occurrence that needs rescheduling."
        reschedule = self.create_occurrence(subscription=self.subscription,
                                             milestone=self.milestone)
        self.occurrence.reschedule = reschedule
        self.occurrence.save()
        replies = MoveHandler.test('APPT MOVE foo bar %s' % self.tomorrow,
                                     identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no future occurrences' in reply)

    def test_prior_occurrence(self):
        "Matched user has no future occurrence."
        self.occurrence.date = self.occurrence.date - timedelta(days=1)
        self.occurrence.save()
        replies = MoveHandler.test('APPT MOVE foo bar %s' % self.tomorrow,
                                     identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no future occurrences' in reply)

    def test_no_subscription(self):
        "Name/ID does not match a subscription."
        self.subscription.delete()
        replies = MoveHandler.test('APPT MOVE foo bar %s' % self.tomorrow,
                                     identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('does not match an active subscription' in reply)

    def test_subscription_ended(self):
        "Name/ID subscription has ended."
        self.subscription.end = now()
        self.subscription.save()
        replies = MoveHandler.test('APPT MOVE foo bar %s' % self.tomorrow,
                                     identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('does not match an active subscription' in reply)


class QuitHandlerTestCase(OccurrenceDataTestCase):
    "Keyword handler for unsubscribing users to timelines"
    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.connection = self.create_connection()
        self.subscription = self.create_timeline_subscription(
            timeline=self.timeline, connection=self.connection, pin='bar')
        QuitHandler._mock_backend = self.connection.backend
        self.prefix = AppointmentHandler.prefix

    def test_help(self):
        "Prefix and keyword should return the help for quitting a subscription."
        replies = QuitHandler.test('APPT QUIT', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(self.prefix + ' QUIT <KEY> <NAME/ID> <DATE>' in reply)

    def test_match(self):
        "Send a successful match to end a timeline subscription."
        replies = QuitHandler.test('APPT QUIT foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_match_with_date(self):
        "Use end date if given."
        end = (now() + timedelta(hours=1)).strftime('%Y-%m-%d')
        replies = QuitHandler.test('APPT QUIT foo bar %s' % end,
                                    identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)
        self.assertEqual(end, TimelineSubscription.objects.all()[0].end.strftime('%Y-%m-%d'))

    def test_no_keyword_match(self):
        "Keyword does not match any existing timelines."
        self.timeline.delete()
        replies = QuitHandler.test('APPT QUIT foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_no_name_given(self):
        "No name is given."
        replies = QuitHandler.test('APPT QUIT foo', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_invalid_date_format_given(self):
        "Invalid date format."
        replies = QuitHandler.test('APPT QUIT foo bar baz', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_already_quit(self):
        "Attempting to unsubscribe and already unsubcribed connection/name pair."
        self.subscription.end = now()
        self.subscription.save()
        replies = QuitHandler.test('APPT QUIT foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))


class SubscribeHandlerTestCase(OccurrenceDataTestCase):
    "Keyword handler for subscribing users to timelines"

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')

    def test_help(self):
        "Keyword should return the help for adding subscriptions."
        replies = SubscribeHandler.test('SUBSCRIBE')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('SUBSCRIBE <KEY> <NAME/ID> <DATE>' in reply)

    def test_match(self):
        "Send a successful match to create user timeline subscription."
        replies = SubscribeHandler.test('SUBSCRIBE foo bar')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_match_with_date(self):
        "Use start date if given."
        tomorrow = (now() + timedelta(days=1)).strftime('%Y-%m-%d')
        replies = SubscribeHandler.test('SUBSCRIBE foo bar %s' % tomorrow)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_match_with_relative_date(self):
        "Use relative start date if given."
        two_weeks_ago = "two weeks ago"
        replies = SubscribeHandler.test('SUBSCRIBE foo bar %s' % two_weeks_ago)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_no_keyword_match(self):
        "Keyword does not match any existing timelines."
        self.timeline.delete()
        replies = SubscribeHandler.test('SUBSCRIBE foo bar')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_no_name_given(self):
        "No name is given."
        replies = SubscribeHandler.test('SUBSCRIBE foo')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_invalid_date_format_given(self):
        "Invalid date format."
        replies = SubscribeHandler.test('SUBSCRIBE foo bar baz')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_already_subscribed(self):
        "Attempting to register and already registered connection/name pair."
        connection = self.create_connection()
        SubscribeHandler._mock_backend = connection.backend
        self.create_timeline_subscription(timeline=self.timeline,
            connection=connection, pin='bar')
        replies = SubscribeHandler.test('SUBSCRIBE foo bar', identity=connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))
        del SubscribeHandler._mock_backend


