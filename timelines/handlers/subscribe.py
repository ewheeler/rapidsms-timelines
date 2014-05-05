from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.utils import formats

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

from ..forms import SubscribeForm


class SubscribeHandler(KeywordHandler):
    "Base keyword handler for the SUB prefix."

    keyword = 'SUBSCRIBE|SUB|ADD'
    form = SubscribeForm
    #success_text = _('Thank you%(user)s! You registered %(phone)s for '
    #                 '%(timeline)s.')
    success_text = _('Thank you! You registered %(phone)s '
                     'for SMS mother reminders and advise')
    help_text = _('To add a phone number to a timeline send: '
                  '%(prefix)s %(keyword)s <KEY> <PHONE>. ')

    #@classmethod
    #def _keyword(cls):
    #    pattern = r"^\s*(?:%s)(?:[\s,;:]+(.+))?$" % cls.prefix
    #    return re.compile(pattern, re.IGNORECASE)

    def parse_message(self, text):
        "Tokenize message text."
        result = {}
        tokens = text.strip().split()
        result['keyword'] = tokens.pop(0)
        if tokens:
            # Next token is the phone number of new subscriber
            result['phone'] = tokens.pop(0)
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
