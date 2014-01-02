# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Timeline'
        db.create_table(u'timelines_timeline', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'timelines', ['Timeline'])

        # Adding model 'TimelineSubscription'
        db.create_table(u'timelines_timelinesubscription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timeline', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'subscribers', to=orm['timelines.Timeline'])),
            ('connection', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'timelines', to=orm['rapidsms.Connection'])),
            ('pin', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
        ))
        db.send_create_signal(u'timelines', ['TimelineSubscription'])

        # Adding model 'Milestone'
        db.create_table(u'timelines_milestone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('timeline', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'milestones', to=orm['timelines.Timeline'])),
            ('offset', self.gf('django.db.models.fields.IntegerField')()),
            ('message', self.gf('django.db.models.fields.CharField')(default=None, max_length=160, null=True, blank=True)),
        ))
        db.send_create_signal(u'timelines', ['Milestone'])

        # Adding model 'Occurrence'
        db.create_table(u'timelines_occurrence', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'occurrences', to=orm['timelines.Milestone'])),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'occurrences', to=orm['timelines.TimelineSubscription'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('reschedule', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'occurrences', null=True, to=orm['timelines.Occurrence'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('notes', self.gf('django.db.models.fields.CharField')(default=u'', max_length=160, blank=True)),
        ))
        db.send_create_signal(u'timelines', ['Occurrence'])

        # Adding model 'Action'
        db.create_table(u'timelines_action', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('occurrence', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'actions', to=orm['timelines.Occurrence'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('attempted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'timelines', ['Action'])

        # Adding model 'Notification'
        db.create_table(u'timelines_notification', (
            (u'action_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['timelines.Action'], unique=True, primary_key=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=160)),
        ))
        db.send_create_signal(u'timelines', ['Notification'])


    def backwards(self, orm):
        # Deleting model 'Timeline'
        db.delete_table(u'timelines_timeline')

        # Deleting model 'TimelineSubscription'
        db.delete_table(u'timelines_timelinesubscription')

        # Deleting model 'Milestone'
        db.delete_table(u'timelines_milestone')

        # Deleting model 'Occurrence'
        db.delete_table(u'timelines_occurrence')

        # Deleting model 'Action'
        db.delete_table(u'timelines_action')

        # Deleting model 'Notification'
        db.delete_table(u'timelines_notification')


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
            'message': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '160', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offset': ('django.db.models.fields.IntegerField', [], {}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'milestones'", 'to': u"orm['timelines.Timeline']"})
        },
        u'timelines.notification': {
            'Meta': {'object_name': 'Notification', '_ormbases': [u'timelines.Action']},
            u'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['timelines.Action']", 'unique': 'True', 'primary_key': 'True'}),
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