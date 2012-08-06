# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'EbuildModel.depend'
        db.add_column('packages_ebuildmodel', 'depend',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EbuildModel.rdepend'
        db.add_column('packages_ebuildmodel', 'rdepend',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EbuildModel.pdepend'
        db.add_column('packages_ebuildmodel', 'pdepend',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'EbuildModel.depend'
        db.delete_column('packages_ebuildmodel', 'depend')

        # Deleting field 'EbuildModel.rdepend'
        db.delete_column('packages_ebuildmodel', 'rdepend')

        # Deleting field 'EbuildModel.pdepend'
        db.delete_column('packages_ebuildmodel', 'pdepend')


    models = {
        'packages.archesmodel': {
            'Meta': {'object_name': 'ArchesModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '22', 'db_index': 'True'})
        },
        'packages.categorymodel': {
            'Meta': {'object_name': 'CategoryModel'},
            'category': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ebuilds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'packages_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'repositories_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'virtual_packages_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'packages.ebuildmodel': {
            'Meta': {'ordering': "('-updated_datetime',)", 'unique_together': "(('package', 'version', 'revision'),)", 'object_name': 'EbuildModel'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'depend': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'eapi': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'ebuild_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ebuild_mtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'homepages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.HomepageModel']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_hard_masked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.LicenseModel']", 'symmetrical': 'False'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.PackageModel']"}),
            'pdepend': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rdepend': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '32', 'null': 'True', 'db_index': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_flags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.UseFlagModel']", 'symmetrical': 'False'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '26', 'db_index': 'True'})
        },
        'packages.herdsmodel': {
            'Meta': {'ordering': "('name',)", 'object_name': 'HerdsModel'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ebuilds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.MaintainerModel']", 'symmetrical': 'False', 'blank': 'True'}),
            'maintainers_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150', 'db_index': 'True'}),
            'packages_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'repositories_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'packages.homepagemodel': {
            'Meta': {'object_name': 'HomepageModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'})
        },
        'packages.keyword': {
            'Meta': {'unique_together': "(('ebuild', 'arch'),)", 'object_name': 'Keyword'},
            'arch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.ArchesModel']"}),
            'ebuild': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.EbuildModel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'packages.licensegroupmodel': {
            'Meta': {'ordering': "('name',)", 'object_name': 'LicenseGroupModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.LicenseModel']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'})
        },
        'packages.licensemodel': {
            'Meta': {'object_name': 'LicenseModel'},
            'ebuilds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'packages.maintainermodel': {
            'Meta': {'ordering': "('name',)", 'object_name': 'MaintainerModel'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ebuilds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'herds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'news_author_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'news_translator_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'packages_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'repositories_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'packages.packagemodel': {
            'Meta': {'ordering': "('-updated_datetime',)", 'unique_together': "(('virtual_package', 'repository'),)", 'object_name': 'PackageModel'},
            'bugs_to': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'changelog': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'changelog_hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'changelog_mtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changelog_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'doc': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ebuilds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.HerdsModel']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_ebuild': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.EbuildModel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.MaintainerModel']", 'symmetrical': 'False', 'blank': 'True'}),
            'manifest_hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'manifest_mtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'metadata_hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.RepositoryModel']"}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'virtual_package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.VirtualPackageModel']"})
        },
        'packages.portagenewsmodel': {
            'Meta': {'ordering': "('-date',)", 'unique_together': "(('name', 'lang'),)", 'object_name': 'PortageNewsModel'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'author_news_set'", 'symmetrical': 'False', 'to': "orm['packages.MaintainerModel']"}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'message_as_html': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'translators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'translator_news_set'", 'symmetrical': 'False', 'to': "orm['packages.MaintainerModel']"}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'packages.remoteid': {
            'Meta': {'object_name': 'RemoteId'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.PackageModel']"}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'packages.repositoryfeedmodel': {
            'Meta': {'unique_together': "(('repository', 'feed'),)", 'object_name': 'RepositoryFeedModel'},
            'feed': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.RepositoryModel']"})
        },
        'packages.repositorymodel': {
            'Meta': {'object_name': 'RepositoryModel'},
            'categories_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ebuilds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'owner_name': ('django.db.models.fields.CharField', [], {'max_length': '65', 'null': 'True', 'blank': 'True'}),
            'packages_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'quality': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'packages.repositorysourcemodel': {
            'Meta': {'object_name': 'RepositorySourceModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repo_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.RepositoryModel']"}),
            'subpath': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'packages.useflagdescriptionmodel': {
            'Meta': {'unique_together': "(('use_flag', 'package'),)", 'object_name': 'UseFlagDescriptionModel'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.VirtualPackageModel']"}),
            'use_flag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.UseFlagModel']"})
        },
        'packages.useflagmodel': {
            'Meta': {'ordering': "('name',)", 'object_name': 'UseFlagModel'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ebuilds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'})
        },
        'packages.virtualpackagemodel': {
            'Meta': {'unique_together': "(('name', 'category'),)", 'object_name': 'VirtualPackageModel'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.CategoryModel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '254', 'db_index': 'True'})
        }
    }

    complete_apps = ['packages']