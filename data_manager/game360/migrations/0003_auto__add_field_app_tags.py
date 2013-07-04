# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'App.tags'
        db.add_column(u'game360_app', 'tags',
                      self.gf('tagging.fields.TagField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'App.tags'
        db.delete_column(u'game360_app', 'tags')


    models = {
        u'game360.app': {
            'Meta': {'object_name': 'App'},
            'appid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tags': ('tagging.fields.TagField', [], {})
        }
    }

    complete_apps = ['game360']