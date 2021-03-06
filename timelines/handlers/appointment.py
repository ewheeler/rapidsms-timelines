from __future__ import unicode_literals

import re

from django.utils.translation import ugettext_lazy as _
from django.utils import formats

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


class AppointmentHandler(KeywordHandler):
    "Base keyword handler for the APPT prefix."

    prefix = 'APPT|APT|REPORT|REP|REGISTER|REG'
    form = None
    success_text = ''

    @classmethod
    def _keyword(cls):
        if hasattr(cls, "keyword"):
            pattern = r"^\s*(?:%s)\s*(?:%s)(?:[\s,;:]+(.+))?$"\
                % (cls.prefix, cls.keyword)
        else:
            pattern = r"^\s*(?:%s)\s*?$" % cls.prefix
        return re.compile(pattern, re.IGNORECASE)

    def handle(self, text):
        "Parse text, validate data, and respond."
        parsed = self.parse_message(text)
        form = self.form(data=parsed, connection=self.msg.connection, msg=self.msg.logger_msg)
        if form.is_valid():
            params = form.save()
            print params
            if 'date' in params:
                params['date'] = formats.date_format(params['date'],
                                                     'SHORT_DATE_FORMAT')
            # TODO separate birth handler!
            """
            if 'patient' in params and params.get('patient') is not None:
                self.respond('Congratulations! Please use id %s for the'
                             ' new child' % params['patient']['id'])
            """
            self.respond(self.success_text % params)
        else:
            error = form.error()
            if error is None:
                self.unknown()
            else:
                self.respond(error)
        return True

    def help(self):
        "Return help mesage."
        if self.help_text:
            keyword = self.keyword.split('|')[0].upper()
            help_text = self.help_text % {'prefix': self.prefix,
                                          'keyword': keyword}
            self.respond(help_text)

    def unknown(self):
        "Common fallback for unknown errors."
        keyword = self.keyword.split('|')[0].upper()
        params = {'prefix': self.prefix, 'keyword': keyword}
        self.respond(_('Sorry, we cannot understand that message. '
                       'For additional help send: %(prefix)s %(keyword)s')
                     % params)
