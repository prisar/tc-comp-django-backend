from app.models import RuleVersion
from app.serializers.base import BaseSerializer
from app.serializers.rule_version import RuleVersionSerializer


class RuleSerializer(BaseSerializer):
    """
    rule serializer
    """
    id = 0
    name = None
    ruleVersions = []

    def __init__(self, rule):
        self.id = rule.id
        self.name = rule.name
        self.ruleVersions = self.get_rule_version_list(rule)

    def get_rule_version_list(self, rule):
        """
        get rule versions by rule object
        :param rule: rule object
        :return: rule version list
        """
        results = list()

        rule_versions = RuleVersion.objects.filter(rule=rule)

        for rule_version in list(rule_versions):
            results.append(RuleVersionSerializer(rule_version).to_dict())

        return results
