#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.apps.base import AppBase
from rapidsms.models import Connection
#from rapidsms.contrib.messagelog.models import Message
from .models import Reporter


class Chat(AppBase):
    def _send_chat_msg(self, msg):
        if msg.contact is None:
            msg.respond('Sorry you must be a registered reporter')
            return
        reporter = Reporter.objects.filter(contact=msg.contact)
        if not reporter:
            msg.respond('Sorry you must be a registered reporter')
            return
        reporter = reporter[0]
        if reporter.facility:
            recipients = set(Connection.objects.filter(
                contact__in=Reporter.objects.filter(
                    facility=reporter.facility).values_list('contact', flat=True)
            ))
        else:
            msg.respond("Sorry, you're not registered to a facility")
        recipients.discard(msg.connection)
        sender = msg.connection.identity
        text = "{0}: {1}".format(sender, msg.text)
        # respond to sender
        sender_text = "sent to {0} members of {1}".format(len(recipients),
                                                          reporter.facility)
        msg.respond(sender_text)
        # 'respond' to group members
        msg.respond(text, connections=list(recipients))

    def handle(self, msg):
        groups = []
        mentions = []
        for token in msg.text.split():
            if token.startswith("#"):
                groups.append(token[1:])
            if token.startswith("@"):
                mentions.append(token[1:])
        groups = [i.lower() for i in groups]
        mentions = [i.lower() for i in mentions]
        if 'chat' in groups or 'chat' in mentions:
            # we got a match for chat send message to guys from
            # sender's facility
            self._send_chat_msg(msg)
        return True
