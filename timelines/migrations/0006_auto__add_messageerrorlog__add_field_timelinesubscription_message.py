# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


def run_file(file_name):
    import os
    f = open(os.path.join(os.path.dirname(__file__), file_name))
    query = f.read()
    db.execute(query)


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MessageErrorLog'
        db.create_table(u'timelines_messageerrorlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'message', to=orm['messagelog.Message'])),
        ))
        db.send_create_signal(u'timelines', ['MessageErrorLog'])

        # Adding field 'TimelineSubscription.message'
        db.add_column(u'timelines_timelinesubscription', 'message',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'timeline_message', null=True, to=orm['messagelog.Message']),
                      keep_default=False)
        run_file("0006_auto__add_messageerrorlog__add_field_timelinesubscription_message.sql")


    def backwards(self, orm):
        # Deleting model 'MessageErrorLog'
        db.delete_table(u'timelines_messageerrorlog')

        # Deleting field 'TimelineSubscription.message'
        db.delete_column(u'timelines_timelinesubscription', 'message_id')
        db.execute("DROP VIEW IF EXISTS reporters")
        db.execute("DROP VIEW IF EXISTS messages_view")


    models = {
        u'messagelog.message': {
            'Meta': {'object_name': 'Message'},
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rapidsms.Connection']", 'null': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rapidsms.Contact']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'rapidsms.backend': {
            'Meta': {'object_name': 'Backend'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        u'rapidsms.connection': {
            'Meta': {'unique_together': "(('backend', 'identity'),)", 'object_name': 'Connection'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rapidsms.Backend']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rapidsms.Contact']", 'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'timelines.action': {
            'Meta': {'object_name': 'Action'},
            'attempted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occurrence': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'actions'", 'to': u"orm['timelines.Occurrence']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'timelines.messageerrorlog': {
            'Meta': {'object_name': 'MessageErrorLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'message'", 'to': u"orm['messagelog.Message']"})
        },
        u'timelines.messageslist': {
            'Meta': {'object_name': 'MessagesList', 'db_table': "u'messages_view'", 'managed': 'False'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'facility': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'village': ('django.db.models.fields.TextField', [], {'default': "u''"})
        },
        u'timelines.milestone': {
            'Meta': {'object_name': 'Milestone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offset': ('django.db.models.fields.IntegerField', [], {}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'milestones'", 'to': u"orm['timelines.Timeline']"})
        },
        u'timelines.milestonetranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'MilestoneTranslation', 'db_table': "u'timelines_milestone_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['timelines.Milestone']"}),
            'message': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '160', 'null': 'True', 'blank': 'True'})
        },
        u'timelines.notification': {
            'Meta': {'object_name': 'Notification', '_ormbases': [u'timelines.Action']},
            u'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['timelines.Action']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'timelines.notificationtranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'NotificationTranslation', 'db_table': "u'timelines_notification_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['timelines.Notification']"}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        u'timelines.occurrence': {
            'Meta': {'ordering': "[u'-date']", 'object_name': 'Occurrence'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'occurrences'", 'to': u"orm['timelines.Milestone']"}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '160', 'blank': 'True'}),
            'reschedule': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'occurrences'", 'null': 'True', 'to': u"orm['timelines.Occurrence']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'occurrences'", 'to': u"orm['timelines.TimelineSubscription']"})
        },
        u'timelines.reporter': {
            'Meta': {'object_name': 'Reporter'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'reporters'", 'unique': 'True', 'to': u"orm['rapidsms.Contact']"}),
            'facility': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'village': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'})
        },
        u'timelines.reporterlist': {
            'Meta': {'object_name': 'ReporterList', 'db_table': "u'reporters'", 'managed': 'False'},
            'created_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'facility': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'village': ('django.db.models.fields.TextField', [], {'default': "u''"})
        },
        u'timelines.timeline': {
            'Meta': {'object_name': 'Timeline'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'timelines.timelinesubscription': {
            'Meta': {'object_name': 'TimelineSubscription'},
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'timelines'", 'to': u"orm['rapidsms.Connection']"}),
            'created_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 6, 6, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'timeline_message'", 'null': 'True', 'to': u"orm['messagelog.Message']"}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'subscriptions'", 'null': 'True', 'to': u"orm['timelines.Reporter']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'subscribers'", 'to': u"orm['timelines.Timeline']"})
        }
    }

    complete_apps = ['timelines']
