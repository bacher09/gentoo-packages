# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PortageNewsModel'
        db.create_table('packages_portagenewsmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=200, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=5, db_index=True)),
            ('revision', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('message_as_html', self.gf('django.db.models.fields.TextField')()),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('packages', ['PortageNewsModel'])

        # Adding unique constraint on 'PortageNewsModel', fields ['name', 'lang']
        db.create_unique('packages_portagenewsmodel', ['name', 'lang'])

        # Adding M2M table for field authors on 'PortageNewsModel'
        db.create_table('packages_portagenewsmodel_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('portagenewsmodel', models.ForeignKey(orm['packages.portagenewsmodel'], null=False)),
            ('maintainermodel', models.ForeignKey(orm['packages.maintainermodel'], null=False))
        ))
        db.create_unique('packages_portagenewsmodel_authors', ['portagenewsmodel_id', 'maintainermodel_id'])

        # Adding M2M table for field translators on 'PortageNewsModel'
        db.create_table('packages_portagenewsmodel_translators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('portagenewsmodel', models.ForeignKey(orm['packages.portagenewsmodel'], null=False)),
            ('maintainermodel', models.ForeignKey(orm['packages.maintainermodel'], null=False))
        ))
        db.create_unique('packages_portagenewsmodel_translators', ['portagenewsmodel_id', 'maintainermodel_id'])

        # Adding model 'HomepageModel'
        db.create_table('packages_homepagemodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('packages', ['HomepageModel'])

        # Adding model 'ArchesModel'
        db.create_table('packages_archesmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=22, db_index=True)),
        ))
        db.send_create_signal('packages', ['ArchesModel'])

        # Adding model 'RepositoryModel'
        db.create_table('packages_repositorymodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('owner_name', self.gf('django.db.models.fields.CharField')(max_length=65, null=True, blank=True)),
            ('owner_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('homepage', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('official', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('quality', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('packages_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('maintainers_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('categories_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('ebuilds_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('packages', ['RepositoryModel'])

        # Adding model 'RepositoryFeedModel'
        db.create_table('packages_repositoryfeedmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.RepositoryModel'])),
            ('feed', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('packages', ['RepositoryFeedModel'])

        # Adding unique constraint on 'RepositoryFeedModel', fields ['repository', 'feed']
        db.create_unique('packages_repositoryfeedmodel', ['repository_id', 'feed'])

        # Adding model 'RepositorySourceModel'
        db.create_table('packages_repositorysourcemodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repo_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('subpath', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.RepositoryModel'])),
        ))
        db.send_create_signal('packages', ['RepositorySourceModel'])

        # Adding model 'CategoryModel'
        db.create_table('packages_categorymodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('metadata_hash', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
            ('virtual_packages_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('packages_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('repositories_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('ebuilds_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('packages', ['CategoryModel'])

        # Adding model 'MaintainerModel'
        db.create_table('packages_maintainermodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75, db_index=True)),
            ('packages_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('herds_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('ebuilds_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('repositories_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('news_author_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('news_translator_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('packages', ['MaintainerModel'])

        # Adding model 'HerdsModel'
        db.create_table('packages_herdsmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150, db_index=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('packages_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('maintainers_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('ebuilds_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('repositories_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('packages', ['HerdsModel'])

        # Adding M2M table for field maintainers on 'HerdsModel'
        db.create_table('packages_herdsmodel_maintainers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('herdsmodel', models.ForeignKey(orm['packages.herdsmodel'], null=False)),
            ('maintainermodel', models.ForeignKey(orm['packages.maintainermodel'], null=False))
        ))
        db.create_unique('packages_herdsmodel_maintainers', ['herdsmodel_id', 'maintainermodel_id'])

        # Adding model 'VirtualPackageModel'
        db.create_table('packages_virtualpackagemodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=254, db_index=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.CategoryModel'])),
        ))
        db.send_create_signal('packages', ['VirtualPackageModel'])

        # Adding unique constraint on 'VirtualPackageModel', fields ['name', 'category']
        db.create_unique('packages_virtualpackagemodel', ['name', 'category_id'])

        # Adding model 'PackageModel'
        db.create_table('packages_packagemodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('virtual_package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.VirtualPackageModel'])),
            ('changelog', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('changelog_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('manifest_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('metadata_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('changelog_mtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('manifest_mtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.RepositoryModel'])),
            ('ebuilds_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('packages', ['PackageModel'])

        # Adding unique constraint on 'PackageModel', fields ['virtual_package', 'repository']
        db.create_unique('packages_packagemodel', ['virtual_package_id', 'repository_id'])

        # Adding M2M table for field herds on 'PackageModel'
        db.create_table('packages_packagemodel_herds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('packagemodel', models.ForeignKey(orm['packages.packagemodel'], null=False)),
            ('herdsmodel', models.ForeignKey(orm['packages.herdsmodel'], null=False))
        ))
        db.create_unique('packages_packagemodel_herds', ['packagemodel_id', 'herdsmodel_id'])

        # Adding M2M table for field maintainers on 'PackageModel'
        db.create_table('packages_packagemodel_maintainers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('packagemodel', models.ForeignKey(orm['packages.packagemodel'], null=False)),
            ('maintainermodel', models.ForeignKey(orm['packages.maintainermodel'], null=False))
        ))
        db.create_unique('packages_packagemodel_maintainers', ['packagemodel_id', 'maintainermodel_id'])

        # Adding model 'UseFlagModel'
        db.create_table('packages_useflagmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ebuilds_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('packages', ['UseFlagModel'])

        # Adding model 'UseFlagDescriptionModel'
        db.create_table('packages_useflagdescriptionmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('use_flag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.UseFlagModel'])),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.VirtualPackageModel'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('packages', ['UseFlagDescriptionModel'])

        # Adding unique constraint on 'UseFlagDescriptionModel', fields ['use_flag', 'package']
        db.create_unique('packages_useflagdescriptionmodel', ['use_flag_id', 'package_id'])

        # Adding model 'LicenseModel'
        db.create_table('packages_licensemodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60, db_index=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True)),
            ('ebuilds_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('packages', ['LicenseModel'])

        # Adding model 'LicenseGroupModel'
        db.create_table('packages_licensegroupmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60, db_index=True)),
        ))
        db.send_create_signal('packages', ['LicenseGroupModel'])

        # Adding M2M table for field licenses on 'LicenseGroupModel'
        db.create_table('packages_licensegroupmodel_licenses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('licensegroupmodel', models.ForeignKey(orm['packages.licensegroupmodel'], null=False)),
            ('licensemodel', models.ForeignKey(orm['packages.licensemodel'], null=False))
        ))
        db.create_unique('packages_licensegroupmodel_licenses', ['licensegroupmodel_id', 'licensemodel_id'])

        # Adding model 'EbuildModel'
        db.create_table('packages_ebuildmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.PackageModel'])),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=26, db_index=True)),
            ('revision', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('license', self.gf('django.db.models.fields.CharField')(max_length=254, blank=True)),
            ('ebuild_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('ebuild_mtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_hard_masked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('eapi', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('slot', self.gf('django.db.models.fields.CharField')(default='0', max_length=32, null=True, db_index=True)),
        ))
        db.send_create_signal('packages', ['EbuildModel'])

        # Adding unique constraint on 'EbuildModel', fields ['package', 'version', 'revision']
        db.create_unique('packages_ebuildmodel', ['package_id', 'version', 'revision'])

        # Adding M2M table for field use_flags on 'EbuildModel'
        db.create_table('packages_ebuildmodel_use_flags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ebuildmodel', models.ForeignKey(orm['packages.ebuildmodel'], null=False)),
            ('useflagmodel', models.ForeignKey(orm['packages.useflagmodel'], null=False))
        ))
        db.create_unique('packages_ebuildmodel_use_flags', ['ebuildmodel_id', 'useflagmodel_id'])

        # Adding M2M table for field licenses on 'EbuildModel'
        db.create_table('packages_ebuildmodel_licenses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ebuildmodel', models.ForeignKey(orm['packages.ebuildmodel'], null=False)),
            ('licensemodel', models.ForeignKey(orm['packages.licensemodel'], null=False))
        ))
        db.create_unique('packages_ebuildmodel_licenses', ['ebuildmodel_id', 'licensemodel_id'])

        # Adding M2M table for field homepages on 'EbuildModel'
        db.create_table('packages_ebuildmodel_homepages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ebuildmodel', models.ForeignKey(orm['packages.ebuildmodel'], null=False)),
            ('homepagemodel', models.ForeignKey(orm['packages.homepagemodel'], null=False))
        ))
        db.create_unique('packages_ebuildmodel_homepages', ['ebuildmodel_id', 'homepagemodel_id'])

        # Adding model 'Keyword'
        db.create_table('packages_keyword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ebuild', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.EbuildModel'])),
            ('arch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.ArchesModel'])),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('packages', ['Keyword'])

        # Adding unique constraint on 'Keyword', fields ['ebuild', 'arch']
        db.create_unique('packages_keyword', ['ebuild_id', 'arch_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Keyword', fields ['ebuild', 'arch']
        db.delete_unique('packages_keyword', ['ebuild_id', 'arch_id'])

        # Removing unique constraint on 'EbuildModel', fields ['package', 'version', 'revision']
        db.delete_unique('packages_ebuildmodel', ['package_id', 'version', 'revision'])

        # Removing unique constraint on 'UseFlagDescriptionModel', fields ['use_flag', 'package']
        db.delete_unique('packages_useflagdescriptionmodel', ['use_flag_id', 'package_id'])

        # Removing unique constraint on 'PackageModel', fields ['virtual_package', 'repository']
        db.delete_unique('packages_packagemodel', ['virtual_package_id', 'repository_id'])

        # Removing unique constraint on 'VirtualPackageModel', fields ['name', 'category']
        db.delete_unique('packages_virtualpackagemodel', ['name', 'category_id'])

        # Removing unique constraint on 'RepositoryFeedModel', fields ['repository', 'feed']
        db.delete_unique('packages_repositoryfeedmodel', ['repository_id', 'feed'])

        # Removing unique constraint on 'PortageNewsModel', fields ['name', 'lang']
        db.delete_unique('packages_portagenewsmodel', ['name', 'lang'])

        # Deleting model 'PortageNewsModel'
        db.delete_table('packages_portagenewsmodel')

        # Removing M2M table for field authors on 'PortageNewsModel'
        db.delete_table('packages_portagenewsmodel_authors')

        # Removing M2M table for field translators on 'PortageNewsModel'
        db.delete_table('packages_portagenewsmodel_translators')

        # Deleting model 'HomepageModel'
        db.delete_table('packages_homepagemodel')

        # Deleting model 'ArchesModel'
        db.delete_table('packages_archesmodel')

        # Deleting model 'RepositoryModel'
        db.delete_table('packages_repositorymodel')

        # Deleting model 'RepositoryFeedModel'
        db.delete_table('packages_repositoryfeedmodel')

        # Deleting model 'RepositorySourceModel'
        db.delete_table('packages_repositorysourcemodel')

        # Deleting model 'CategoryModel'
        db.delete_table('packages_categorymodel')

        # Deleting model 'MaintainerModel'
        db.delete_table('packages_maintainermodel')

        # Deleting model 'HerdsModel'
        db.delete_table('packages_herdsmodel')

        # Removing M2M table for field maintainers on 'HerdsModel'
        db.delete_table('packages_herdsmodel_maintainers')

        # Deleting model 'VirtualPackageModel'
        db.delete_table('packages_virtualpackagemodel')

        # Deleting model 'PackageModel'
        db.delete_table('packages_packagemodel')

        # Removing M2M table for field herds on 'PackageModel'
        db.delete_table('packages_packagemodel_herds')

        # Removing M2M table for field maintainers on 'PackageModel'
        db.delete_table('packages_packagemodel_maintainers')

        # Deleting model 'UseFlagModel'
        db.delete_table('packages_useflagmodel')

        # Deleting model 'UseFlagDescriptionModel'
        db.delete_table('packages_useflagdescriptionmodel')

        # Deleting model 'LicenseModel'
        db.delete_table('packages_licensemodel')

        # Deleting model 'LicenseGroupModel'
        db.delete_table('packages_licensegroupmodel')

        # Removing M2M table for field licenses on 'LicenseGroupModel'
        db.delete_table('packages_licensegroupmodel_licenses')

        # Deleting model 'EbuildModel'
        db.delete_table('packages_ebuildmodel')

        # Removing M2M table for field use_flags on 'EbuildModel'
        db.delete_table('packages_ebuildmodel_use_flags')

        # Removing M2M table for field licenses on 'EbuildModel'
        db.delete_table('packages_ebuildmodel_licenses')

        # Removing M2M table for field homepages on 'EbuildModel'
        db.delete_table('packages_ebuildmodel_homepages')

        # Deleting model 'Keyword'
        db.delete_table('packages_keyword')


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
            'changelog': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'changelog_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'changelog_mtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ebuilds_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.HerdsModel']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['packages.MaintainerModel']", 'symmetrical': 'False', 'blank': 'True'}),
            'manifest_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'manifest_mtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'metadata_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
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
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'translators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'translator_news_set'", 'symmetrical': 'False', 'to': "orm['packages.MaintainerModel']"}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
