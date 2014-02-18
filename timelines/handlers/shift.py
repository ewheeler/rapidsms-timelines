from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from ..forms import ShiftForm


class ShiftHandler(KeywordHandler):
    "Shift timeline for a subscriber"

    keyword = 'shift'
    form = ShiftForm
    help_text = _('To shift subscription dates send: %(prefix)s %(keyword)s <KEY> <NAME/ID> <DATE>')
    success_text = _('Thank you! The timeline has been shifted and future occurences have been rescheduled.')

    def parse_message(self, text):
        "Tokenize message text."
        result = {}
        tokens = text.strip().split()
        result['keyword'] = tokens.pop(0)
        if tokens:
            # Next token is the name/id
            result['name'] = tokens.pop(0)
            if tokens:
                # Remaining tokens should be a date string
                result['date'] = ' '.join(tokens)
        return result

    def handle(self, text):
        "Parse text, validate data, and respond."
        parsed = self.parse_message(text)
        form = self.form(data=parsed, connection=self.msg.connection)
        if form.is_valid():
            params = form.save()
            if 'date' in params:
                params['date'] = formats.date_format(params['date'],
                                                     'SHORT_DATE_FORMAT')
            self.respond(self.success_text % params)
        else:
            error = form.error()
            if error is None:
                self.unknown()
            else:
                self.respond(error)
        return True
