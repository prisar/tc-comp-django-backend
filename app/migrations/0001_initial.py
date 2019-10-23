# Generated by Django 2.2.6 on 2019-10-08 05:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
            options={
                'db_table': 'projects',
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
            options={
                'db_table': 'rules',
            },
        ),
        migrations.CreateModel(
            name='RuleVersion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('version_number', models.CharField(max_length=128)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('state', models.CharField(max_length=45)),
                ('text', models.TextField()),
                ('specific_test', models.TextField()),
                ('test_category', models.TextField()),
                ('test_type', models.TextField()),
                ('is_locked', models.BooleanField(default=False)),
                ('locked_by_user_id', models.IntegerField(default=0)),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Rule')),
            ],
            options={
                'db_table': 'rule_versions',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=16, unique=True)),
                ('email', models.CharField(max_length=255, null=True)),
                ('password', models.CharField(max_length=32)),
                ('thumbnail_url', models.CharField(max_length=255, null=True)),
                ('role', models.CharField(max_length=8)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Vin',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
            options={
                'db_table': 'vins',
            },
        ),
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.User')),
            ],
            options={
                'db_table': 'workspaces',
            },
        ),
        migrations.CreateModel(
            name='RuleVersionNote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('notes', models.TextField()),
                ('rule_version', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.RuleVersion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.User')),
            ],
            options={
                'db_table': 'rule_version_notes',
            },
        ),
        migrations.AddField(
            model_name='ruleversion',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.User'),
        ),
        migrations.CreateModel(
            name='WorkspacesRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Rule')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Workspace')),
            ],
            options={
                'db_table': 'workspaces_rules',
                'unique_together': {('workspace', 'rule')},
            },
        ),
        migrations.CreateModel(
            name='WorkspacesProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Project')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Workspace')),
            ],
            options={
                'db_table': 'workspaces_projects',
                'unique_together': {('workspace', 'project')},
            },
        ),
        migrations.CreateModel(
            name='WorkspacesMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.User')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Workspace')),
            ],
            options={
                'db_table': 'workspaces_members',
                'unique_together': {('workspace', 'user')},
            },
        ),
        migrations.CreateModel(
            name='RuleVersionNode',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('node_id', models.IntegerField()),
                ('rule_text', models.TextField()),
                ('parent_id', models.IntegerField(null=True)),
                ('rule_version', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.RuleVersion')),
            ],
            options={
                'db_table': 'rule_version_nodes',
                'unique_together': {('rule_version', 'id')},
            },
        ),
        migrations.CreateModel(
            name='RuleVersionHasVin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_version', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.RuleVersion')),
                ('vins', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Vin')),
            ],
            options={
                'db_table': 'rule_version_has_vins',
                'unique_together': {('rule_version', 'vins')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='ruleversion',
            unique_together={('rule', 'version_number')},
        ),
        migrations.CreateModel(
            name='ProjectsHasVin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Project')),
                ('vin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Vin')),
            ],
            options={
                'db_table': 'projects_has_vins',
                'unique_together': {('project', 'vin')},
            },
        ),
    ]
