# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Appointment'
        db.delete_table(u'appointments_appointment')

        # Adding model 'Action'
        db.create_table(u'appointments_action', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('occurrence', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'actions', to=orm['appointments.Occurrence'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('attempted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'appointments', ['Action'])

        # Adding model 'Occurrence'
        db.create_table(u'appointments_occurrence', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'occurrences', to=orm['appointments.Milestone'])),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'occurrences', to=orm['appointments.TimelineSubscription'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('notes', self.gf('django.db.models.fields.CharField')(default=u'', max_length=160, blank=True)),
        ))
        db.send_create_signal(u'appointments', ['Occurrence'])

        # Deleting field 'Notification.status'
        db.delete_column(u'appointments_notification', 'status')

        # Deleting field 'Notification.confirmed'
        db.delete_column(u'appointments_notification', 'confirmed')

        # Deleting field 'Notification.appointment'
        db.delete_column(u'appointments_notification', 'appointment_id')

        # Deleting field 'Notification.id'
        db.delete_column(u'appointments_notification', u'id')

        # Deleting field 'Notification.sent'
        db.delete_column(u'appointments_notification', 'sent')

        # Adding field 'Notification.action_ptr'
        db.add_column(u'appointments_notification', u'action_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['appointments.Action'], unique=True, primary_key=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'Appointment'
        db.create_table(u'appointments_appointment', (
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('confirmed', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'appointments', to=orm['appointments.Milestone'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('notes', self.gf('django.db.models.fields.CharField')(default=u'', max_length=160, blank=True)),
            ('reschedule', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'appointments', null=True, to=orm['appointments.Appointment'], blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'appointments', to=orm['appointments.TimelineSubscription'])),
        ))
        db.send_create_signal(u'appointments', ['Appointment'])

        # Deleting model 'Action'
        db.delete_table(u'appointments_action')

        # Deleting model 'Occurrence'
        db.delete_table(u'appointments_occurrence')

        # Adding field 'Notification.status'
        db.add_column(u'appointments_notification', 'status',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Notification.confirmed'
        db.add_column(u'appointments_notification', 'confirmed',
                      self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Notification.appointment'
        raise RuntimeError("Cannot reverse this migration. 'Notification.appointment' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Notification.appointment'
        db.add_column(u'appointments_notification', 'appointment',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'notifications', to=orm['appointments.Appointment']),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Notification.id'
        raise RuntimeError("Cannot reverse this migration. 'Notification.id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Notification.id'
        db.add_column(u'appointments_notification', u'id',
                      self.gf('django.db.models.fields.AutoField')(primary_key=True),
                      keep_default=False)

        # Adding field 'Notification.sent'
        db.add_column(u'appointments_notification', 'sent',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Notification.action_ptr'
        db.delete_column(u'appointments_notification', u'action_ptr_id')


    models = {
        u'appointments.action': {
            'Meta': {'object_name': 'Action'},
            'attempted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occurrence': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'actions'", 'to': u"orm['appointments.Occurrence']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'})
        },
        u'appointments.milestone': {
            'Meta': {'object_name': 'Milestone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offset': ('django.db.models.fields.IntegerField', [], {}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'milestones'", 'to': u"orm['appointments.Timeline']"})
        },
        u'appointments.notification': {
            'Meta': {'object_name': 'Notification', '_ormbases': [u'appointments.Action']},
            u'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['appointments.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        u'appointments.occurrence': {
            'Meta': {'ordering': "[u'-date']", 'object_name': 'Occurrence'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'occurrences'", 'to': u"orm['appointments.Milestone']"}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '160', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'occurrences'", 'to': u"orm['appointments.TimelineSubscription']"})
        },
        u'appointments.timeline': {
            'Meta': {'object_name': 'Timeline'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'appointments.timelinesubscription': {
            'Meta': {'object_name': 'TimelineSubscription'},
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'timelines'", 'to': u"orm['rapidsms.Connection']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'subscribers'", 'to': u"orm['appointments.Timeline']"})
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
        }
    }

    complete_apps = ['appointments']