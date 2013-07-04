# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'App'
        db.create_table(u'game360_app', (
            ('appid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tags', self.gf('tagging.fields.TagField')()),
        ))
        db.send_create_signal(u'game360', ['App'])


    def backwards(self, orm):
        # Deleting model 'App'
        db.delete_table(u'game360_app')


    models = {
        u'game360.app': {
            'Meta': {'object_name': 'App'},
            'appid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tags': ('tagging.fields.TagField', [], {})
        }
    }

    complete_apps = ['game360']