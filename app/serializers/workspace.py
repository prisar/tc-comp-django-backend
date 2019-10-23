from app.serializers.base import BaseSerializer
from app.models import WorkspacesRule, WorkspacesProject, WorkspacesMember


class WorkspaceSerializer(BaseSerializer):
    """
    workspace serializer
    """
    id = 0
    name = None
    ownerUserId = 0
    memberUserIds = []
    ruleIds = []
    projectIds = []

    def __init__(self, workspace):
        self.id = workspace.id
        self.name = workspace.name
        self.ownerUserId = workspace.user.id
        self.memberUserIds = self.get_member_id_list(workspace)
        self.projectIds = self.get_project_id_list(workspace)
        self.ruleIds = self.get_rule_id_list(workspace)

    def get_member_id_list(self, workspace):
        """
        get member id list
        :param workspace: workspace object
        :return: member id list
        """
        results = list()
        workspace_members = WorkspacesMember.objects.filter(workspace=workspace)

        for workspace_member in list(workspace_members):
            results.append(workspace_member.user.id)

        return results

    def get_project_id_list(self, workspace):
        """
        get project id list
        :param workspace: workspace object
        :return: project id list
        """
        results = list()
        workspace_projects = WorkspacesProject.objects.filter(workspace=workspace)

        for workspace_project in list(workspace_projects):
            results.append(workspace_project.project.id)

        return results

    def get_rule_id_list(self, workspace):
        """
        get rule id list
        :param workspace: workspace object
        :return: rule id list
        """
        results = list()
        workspace_rules = WorkspacesRule.objects.filter(workspace=workspace)

        for workspace_rule in list(workspace_rules):
            results.append(workspace_rule.rule.id)

        return results