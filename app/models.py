from django.db import models


class Rule(models.Model):
    """
    Rule model
    """
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = 'rules'


class User(models.Model):
    """
    User model
    """
    id = models.AutoField(null=False, primary_key=True)
    name = models.CharField(max_length=16, null=False)
    email = models.CharField(max_length=255, null=False, unique=True)
    password = models.CharField(max_length=32, null=False)
    thumbnail_url = models.CharField(max_length=255, null=True)
    role = models.CharField(max_length=8)

    class Meta:
        db_table = 'users'


class Workspace(models.Model):
    """
    Workspace model
    """
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        db_table = 'workspaces'


class Project(models.Model):
    """
    Project model
    """
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = 'projects'


class Vin(models.Model):
    """
    VIN model
    """
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = 'vins'


class RuleVersion(models.Model):
    """
    RuleVersion model
    """
    id = models.AutoField(primary_key=True, null=False)
    rule = models.ForeignKey(Rule, null=False, on_delete=models.PROTECT)
    version_number = models.CharField(max_length=128, null=False)
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    date_created = models.DateField(auto_now_add=True, null=False)
    date_modified = models.DateField(auto_now=True, null=False)
    state = models.CharField(max_length=45, null=False)
    text = models.TextField()
    specific_test = models.TextField()
    test_category = models.TextField()
    test_type = models.TextField()
    is_locked = models.BooleanField(default=False, null=False)
    locked_by_user_id = models.IntegerField(default=0, null=False)

    class Meta:
        unique_together = (('rule', 'version_number'),)
        db_table = 'rule_versions'


class ProjectsHasVin(models.Model):
    """
    Project and vin mapping model
    """
    project = models.ForeignKey(Project, null=False, on_delete=models.PROTECT)
    vin = models.ForeignKey(Vin, null=False, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('project', 'vin'), )
        db_table = 'projects_has_vins'


class RuleVersionHasVin(models.Model):
    """
    RuleVersionHasVin model
    """
    rule_version = models.ForeignKey(RuleVersion, null=False, on_delete=models.PROTECT)
    vins = models.ForeignKey(Vin, null=False, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('rule_version', 'vins'), )
        db_table = 'rule_version_has_vins'


class RuleVersionNode(models.Model):
    """
    RuleVersionNode model
    """
    id = models.AutoField(primary_key=True, null=False)
    node_id = models.IntegerField(null=False)
    rule_text = models.TextField(null=False)
    rule_version = models.ForeignKey(RuleVersion, null=False, on_delete=models.PROTECT)
    parent_id = models.IntegerField(null=True)

    class Meta:
        unique_together = (('rule_version', 'id'), )
        db_table = 'rule_version_nodes'


class RuleVersionNote(models.Model):
    """
    RuleVersionNote model
    """
    id = models.AutoField(primary_key=True, null=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateField(auto_now_add=True, null=False)
    rule_version = models.ForeignKey(RuleVersion, null=False, on_delete=models.PROTECT)
    notes = models.TextField(null=False)

    class Meta:
        db_table = 'rule_version_notes'


class WorkspacesProject(models.Model):
    """
    Workspace and project mapping model
    """
    workspace = models.ForeignKey(Workspace, null=False, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, null=False, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('workspace', 'project'), )
        db_table = 'workspaces_projects'


class WorkspacesMember(models.Model):
    """
    Workspace and member mapping model
    """
    workspace = models.ForeignKey(Workspace, null=False, on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('workspace', 'user'), )
        db_table = 'workspaces_members'


class WorkspacesRule(models.Model):
    """
    Workspace and rule mapping model
    """
    workspace = models.ForeignKey(Workspace, null=False, on_delete=models.PROTECT)
    rule = models.ForeignKey(Rule, null=False, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('workspace', 'rule'), )
        db_table = 'workspaces_rules'
