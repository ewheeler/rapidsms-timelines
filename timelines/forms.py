from __future__ import unicode_literals

from django import forms
from django.db.models import Q
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.models import model_to_dict
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from rapidsms.models import Connection
from rapidsms.models import Backend

from healthcare.api import client

from .models import Timeline
from .models import TimelineSubscription
from .models import Occurrence
from .models import Notification
from .models import now


class PlainErrorList(ErrorList):
    "Customization of the error list for including in an SMS message."

    def as_text(self):
        if not self:
            return ''
        return ''.join(['%s' % force_unicode(e) for e in self])


class HandlerForm(forms.Form):
    "Base form class for validating SMS handler message data."

    keyword = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop('connection', None)
        kwargs['error_class'] = PlainErrorList
        super(HandlerForm, self).__init__(*args, **kwargs)

    def clean_keyword(self):
        "Check if this keyword is associated with any timeline."
        keyword = self.cleaned_data.get('keyword', '')
        match = None
        if keyword:
            # Query DB for valid keywords
            for timeline in Timeline.objects.filter(slug__icontains=keyword):
                if keyword.strip().lower() in timeline.keywords:
                    match = timeline
                    break
        if match is None:
            # Invalid keyword
            raise forms.ValidationError(_('Sorry, we could not find '
                    'any occurrences for the keyword: %s') % keyword)
        else:
            self.cleaned_data['timeline'] = match
        return keyword

    def error(self):
        "Condense form errors to single error message."
        errors = self.errors
        error = None
        if self.errors:
            # Return first field error based on field order
            for field in self.fields:
                if field in errors:
                    error = errors[field].as_text()
                    break
            if error is None and NON_FIELD_ERRORS in errors:
                error = self.errors[NON_FIELD_ERRORS].as_text()
        return error

    def save(self):
        "Update necessary data and return parameters for the success message."
        return {}


class NewForm(HandlerForm):
    "Register user for new timeline."

    name = forms.CharField(error_messages={
        'required': _('Sorry, you must include a name or id for your '
                      'occurrences subscription.')
    })
    date = forms.DateTimeField(required=False, error_messages={
        'invalid': _('Sorry, we cannot understand that date format. '
                     'For the best results please use the ISO '
                     'YYYY-MM-DD format.')
    })

    def clean(self):
        "Check for previous subscription."
        timeline = self.cleaned_data.get('timeline', None)
        name = self.cleaned_data.get('name', None)
        if name is not None and timeline is not None:
            previous = TimelineSubscription.objects.filter(
                Q(Q(end__isnull=True) | Q(end__gte=now())),
                timeline=timeline, connection=self.connection, pin=name
            )
            if previous.exists():
                params = {'timeline': timeline.name, 'name': name}
                message = _('Sorry, you previously registered a %(timeline)s '
                            'for %(name)s. You will be notified when '
                            'it is time for the next occurrence.') % params
                raise forms.ValidationError(message)
        return self.cleaned_data

    def save(self):
        if not self.is_valid():
            return None
        timeline = self.cleaned_data['timeline']
        name = self.cleaned_data['name']
        start = self.cleaned_data.get('date', now()) or now()
        # FIXME: There is a small race condition here that we could
        # create two subscriptions in parallel
        TimelineSubscription.objects.create(
            timeline=timeline, start=start, pin=name,
            connection=self.connection
        )
        # FIXME: better matching
        patient = None
        if timeline == Timeline.objects.get(name='New Birth/Postnatal Care Visits'):
            patient = client.patients.create(birthdate=start.date())

        user = ' %s' % self.connection.contact.name if self.connection.contact else ''
        return {
            'user': user,
            'date': start,
            'name': name,
            'timeline': timeline.name,
            'patient': patient,
        }


class SubscribeForm(HandlerForm):
    "Register a phone for new timeline."

    phone = forms.CharField(error_messages={
        'required': _('Sorry, you must include a phone number for your '
                      'subscription.')
    })

    keyword = forms.CharField(error_messages={
        'required': _('Sorry, you must include the name of the timeilne for your '
                      'subscription.')
    })

    def clean(self):
        "Check for previous subscription."
        timeline = self.cleaned_data.get('timeline', None)
        phone = self.cleaned_data.get('phone', None)
        # TODO how to choose backend?
        backend = Backend.objects.get(name='default')
        self.connection, created = Connection.objects.get_or_create(identity=phone,
                                                               backend=backend)
        if phone is not None and timeline is not None:
            previous = TimelineSubscription.objects.filter(
                Q(Q(end__isnull=True) | Q(end__gte=now())),
                timeline=timeline, connection=self.connection, pin=phone
            )
            if previous.exists():
                params = {'timeline': timeline.name, 'phone': phone}
                message = _('Sorry, you previously registered %(phone)s '
                            'for %(timeline)s. They will continue to receive '
                            'messages.') % params
                raise forms.ValidationError(message)
        print self.cleaned_data
        return self.cleaned_data

    def save(self):
        print 'SAVE'
        if not self.is_valid():
            print 'INVALID'
            return None
        print 'VALID'
        timeline = self.cleaned_data['timeline']
        phone = self.cleaned_data['phone']
        start = now()
        # FIXME: There is a small race condition here that we could
        # create two subscriptions in parallel
        TimelineSubscription.objects.create(
            timeline=timeline, start=start, pin=phone,
            connection=self.connection
        )
        user = ' %s' % self.connection.contact.name if self.connection.contact else ''
        return {
            'user': user,
            'phone': phone,
            'timeline': timeline.name,
        }


class ConfirmForm(HandlerForm):
    "Confirm an upcoming occurrence."

    name = forms.CharField()

    def clean_name(self):
        "Find last uncompleted notification for upcoming occurrence."
        timeline = self.cleaned_data.get('timeline', None)
        name = self.cleaned_data.get('name', '')
        # name should be a pin for an active timeline subscription
        timelines = TimelineSubscription.objects.filter(
            Q(Q(end__gte=now()) | Q(end__isnull=True)),
            timeline=timeline, connection=self.connection, pin=name
        ).values_list('timeline', flat=True)
        if not timelines:
            # PIN doesn't match an active subscription for this connection
            raise forms.ValidationError(_('Sorry, name/id does not match '
                                          'an active subscription.'))
        try:
            notification = Notification.objects.filter(
                status=Notification.STATUS_PENDING,
                completed__isnull=True,
                occurrence__completed__isnull=True,
                occurrence__reschedule__isnull=True,
                occurrence__date__gte=now(),
                occurrence__milestone__timeline__in=timelines
            ).order_by('-attempted')[0]
        except IndexError:
            # No uncompleted notifications
            raise forms.ValidationError(_('Sorry, you have no uncompleted '
                                          'occurrence notifications.'))
        else:
            self.cleaned_data['notification'] = notification
        return name

    def save(self):
        "Mark the current notification as completed and return it."
        if not self.is_valid():
            return None
        notification = self.cleaned_data['notification']
        notification.confirm()
        return {}


class StatusForm(HandlerForm):
    "Set the status of an occurrence that a patient was seen"

    name = forms.CharField()
    status = forms.CharField()

    def clean_status(self):
        "Map values from inbound messages to Occurrence.STATUS_CHOICES"
        raw_status = self.cleaned_data.get('status', '')
        valid_status_update = Occurrence.STATUS_CHOICES[1:]
        status = next((x[0] for x in valid_status_update
                       if x[1].upper() == raw_status.upper()), None)
        if not status:
            choices = tuple([x[1].upper() for x in valid_status_update])
            params = {'choices': ', '.join(choices), 'raw_status': raw_status}
            msg = _('Sorry, the status update must be in %(choices)s. '
                    'You supplied %(raw_status)s') % params
            raise forms.ValidationError(msg)
        return status

    def clean_name(self):
        "Find the most recent occurrence for the patient."
        timeline = self.cleaned_data.get('timeline', None)
        name = self.cleaned_data.get('name', '')
        # name should be a pin for an active timeline subscription
        timelines = TimelineSubscription.objects.filter(
            Q(Q(end__gte=now()) | Q(end__isnull=True)),
            timeline=timeline, connection=self.connection, pin=name
        ).values_list('timeline', flat=True)
        if not timelines:
            # PIN doesn't match an active subscription for this connection
            raise forms.ValidationError(_('Sorry, name/id does not match '
                                          'an active subscription.'))
        try:
            occurrence = Occurrence.objects.filter(
                status=Occurrence.STATUS_DEFAULT,
                date__lte=now(),
                milestone__timeline__in=timelines
            ).order_by('-date')[0]
        except IndexError:
            # No recent occurrence that is not STATUS_DEFAULT
            msg = _('Sorry, user has no recent occurrences that require '
                    'a status update.')
            raise forms.ValidationError(msg)
        else:
            self.cleaned_data['occurrence'] = occurrence
        return name

    def save(self):
        "Mark the occurrence status and return it"
        if not self.is_valid():
            return None
        occurrence = self.cleaned_data['occurrence']
        occurrence.status = self.cleaned_data['status']
        occurrence.save()
        return {}


class MoveForm(HandlerForm):
    "Reschedule the next upcoming occurrence for a patient"

    name = forms.CharField()
    date = forms.DateTimeField(error_messages={
        'invalid': _('Sorry, we cannot understand that date format. '
                     'For the best results please use the '
                     'ISO YYYY-MM-DD format.')
    })

    def clean_date(self):
        "Ensure the date to reschedule is in the future"
        date = self.cleaned_data.get('date')
        # date should be in the future
        if date and date.date() < now().date():
            raise forms.ValidationError(_('Sorry, the reschedule date %s must '
                                          'be in the future') % date)
        return date

    def clean_name(self):
        "Find the next occurrence for the patient."
        timeline = self.cleaned_data.get('timeline', None)
        name = self.cleaned_data.get('name', '')
        # name should be a pin for an active timeline subscription
        timelines = TimelineSubscription.objects.filter(
            Q(Q(end__gte=now()) | Q(end__isnull=True)),
            timeline=timeline, connection=self.connection, pin=name
        ).values_list('timeline', flat=True)
        if not timelines:
            # PIN doesn't match an active subscription for this connection
            raise forms.ValidationError(_('Sorry, name/id does not match '
                                          'an active subscription.'))
        try:
            occurrence = Occurrence.objects.filter(
                status=Occurrence.STATUS_DEFAULT,
                date__gte=now(),
                milestone__timeline__in=timelines,
                reschedule__isnull=True,
                occurrences__isnull=True,
            ).order_by('-date')[0]
        except IndexError:
            # No future occurrence
            msg = _('Sorry, user has no future occurrences that '
                    'require a reschedule.')
            raise forms.ValidationError(msg)
        else:
            self.cleaned_data['occurrence'] = occurrence
        return name

    def save(self):
        "Mark the occurrence status and return it"
        if not self.is_valid():
            return None
        occurrence = self.cleaned_data['occurrence']
        #serialize the old occurrence values
        params = model_to_dict(occurrence)
        #overwrite the date w/ reschedule data
        params['date'] = self.cleaned_data['date']
        params.pop('id')
        params['milestone'] = occurrence.milestone
        params['subscription'] = occurrence.subscription
        reschedule = Occurrence.objects.create(**params)
        occurrence.reschedule = reschedule
        occurrence.save()
        return {}


class QuitForm(HandlerForm):
    "Unsubscribes a user from a timeline by populating the end date."

    keyword = forms.CharField()
    name = forms.CharField(error_messages={
        'required': _('Sorry, you must include a name or id for your '
                      'unsubscription.')
    })
    date = forms.DateTimeField(required=False, error_messages={
        'invalid': _('Sorry, we cannot understand that date format. '
                     'For the best results please use the '
                     'ISO YYYY-MM-DD format.')
    })

    def clean_keyword(self):
        "Check if this keyword is associated with any timeline."
        keyword = self.cleaned_data.get('keyword', '')
        match = None
        if keyword:
            # Query DB for valid keywords
            for timeline in Timeline.objects.filter(slug__icontains=keyword):
                if keyword.strip().lower() in timeline.keywords:
                    match = timeline
                    break
        if match is None:
            # Invalid keyword
            raise forms.ValidationError(_('Sorry, we could not find any '
                                          'occurrences for the keyword: %s')
                                        % keyword)
        else:
            self.cleaned_data['timeline'] = match
        return keyword

    def clean(self):
        "Check for previous subscription."
        timeline = self.cleaned_data.get('timeline', None)
        name = self.cleaned_data.get('name', None)
        if name is not None and timeline is not None:
            previous = TimelineSubscription.objects.filter(
                Q(Q(end__isnull=True) | Q(end__gte=now())),
                timeline=timeline, connection=self.connection, pin=name
            )
            if not previous.exists():
                params = {'timeline': timeline.name, 'name': name}
                message = _('Sorry, you have not registered a %(timeline)s '
                            'for %(name)s.') % params
                raise forms.ValidationError(message)
            self.cleaned_data['subscription'] = previous[0]
        return self.cleaned_data

    def save(self):
        if not self.is_valid():
            return None
        subscription = self.cleaned_data['subscription']
        name = self.cleaned_data['name']
        end = self.cleaned_data.get('date', now()) or now()
        user = ' %s' % self.connection.contact.name if self.connection.contact else ''
        subscription.end = end
        subscription.save()
        return {
            'user': user,
            'date': end,
            'name': name,
            'timeline': subscription.timeline.name,
        }


def get_pins():
    pins = sorted([(x, x) for x in TimelineSubscription.objects.all().values_list('pin', flat=True)])
    return pins


class OccurrenceFilterForm(forms.Form):
    completed = [('false', 'Yes'), ('true', 'No')]

    def __init__(self, *args, **kwargs):
        super(OccurrenceFilterForm, self).__init__(*args, **kwargs)
        pin_choices = [('', 'All')] + get_pins()
        pin_field = self.fields['subscription__pin']
        pin_field.choices = pin_choices

    subscription__timeline = forms.ModelChoiceField(queryset=Timeline.objects.all(),
                                                    empty_label=_("All"),
                                                    label=_("Timeline"),
                                                    required=False)

    subscription__pin = forms.ChoiceField(choices=[('', 'All')],
                                          label=_("Pin"),
                                          required=False)
    status = forms.ChoiceField(choices=[('', 'All')] + Occurrence.STATUS_CHOICES,
                               required=False)

    completed__isnull = forms.ChoiceField(choices=[('', 'All')] + completed,
                                          label=_("Completed"),
                                          required=False)

    def clean_completed__isnull(self):
        completed = self.cleaned_data.get('completed__isnull', None)
        if completed:
            completed = False if completed == 'false' else True
        return completed

    def get_items(self):
        if self.is_valid():
            filters = dict([(k, v) for k, v in self.cleaned_data.iteritems() if v or v is False])
            return Occurrence.objects.filter(**filters)
        return Occurrence.objects.none()
