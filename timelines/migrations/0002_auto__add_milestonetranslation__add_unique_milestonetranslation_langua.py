# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MilestoneTranslation'
        db.create_table(u'timelines_milestone_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.CharField')(default=None, max_length=160, null=True, blank=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['timelines.Milestone'])),
        ))
        db.send_create_signal(u'timelines', ['MilestoneTranslation'])

        # Adding unique constraint on 'MilestoneTranslation', fields ['language_code', 'master']
        db.create_unique(u'timelines_milestone_translation', ['language_code', 'master_id'])

        # Adding model 'NotificationTranslation'
        db.create_table(u'timelines_notification_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['timelines.Notification'])),
        ))
        db.send_create_signal(u'timelines', ['NotificationTranslation'])

        # Adding unique constraint on 'NotificationTranslation', fields ['language_code', 'master']
        db.create_unique(u'timelines_notification_translation', ['language_code', 'master_id'])

        # Deleting field 'Notification.message'
        db.delete_column(u'timelines_notification', 'message')

        # Deleting field 'Milestone.message'
        db.delete_column(u'timelines_milestone', 'message')


    def backwards(self, orm):
        # Removing unique constraint on 'NotificationTranslation', fields ['language_code', 'master']
        db.delete_unique(u'timelines_notification_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'MilestoneTranslation', fields ['language_code', 'master']
        db.delete_unique(u'timelines_milestone_translation', ['language_code', 'master_id'])

        # Deleting model 'MilestoneTranslation'
        db.delete_table(u'timelines_milestone_translation')

        # Deleting model 'NotificationTranslation'
        db.delete_table(u'timelines_notification_translation')


        # User chose to not deal with backwards NULL issues for 'Notification.message'
        raise RuntimeError("Cannot reverse this migration. 'Notification.message' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Notification.message'
        db.add_column(u'timelines_notification', 'message',
                      self.gf('django.db.models.fields.CharField')(max_length=160),
                      keep_default=False)

        # Adding field 'Milestone.message'
        db.add_column(u'timelines_milestone', 'message',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=160, null=True, blank=True),
                      keep_default=False)


    models = {
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
        u'timelines.timeline': {
            'Meta': {'object_name': 'Timeline'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'timelines.timelinesubscription': {
            'Meta': {'object_name': 'TimelineSubscription'},
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'timelines'", 'to': u"orm['rapidsms.Connection']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'subscribers'", 'to': u"orm['timelines.Timeline']"})
        }
    }

    complete_apps = ['timelines']