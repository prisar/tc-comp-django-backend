from app.models import RuleVersionNode, RuleVersionNote, RuleVersionHasVin, Vin
from app.serializers.base import BaseSerializer
from app.serializers.rule_version_node import RuleVersionNodeSerializer
from app.serializers.rule_version_note import RuleVersionNoteSerializer
from app.serializers.vin import VinSerializer


class RuleVersionSerializer(BaseSerializer):
    """
    rule version serializer
    """
    id = 0
    parentRuleId = 0
    versionNumber = None
    authorUserId = 0
    authorUserName = None
    ruleTree = []
    enabledVins = []
    dateCreated = None
    dateModified = None
    state = None
    text = None
    specificTest = None
    testCategory = None
    testType = None
    notes = []
    lock = {
        'isLocked': False,
        'lockedByUserId': 0,
    }

    def __init__(self, rule_version):
        self.id = rule_version.id
        self.parentRuleId = rule_version.rule.id
        self.versionNumber = rule_version.version_number
        self.authorUserId = rule_version.user.id
        self.authorUserName = rule_version.user.name
        self.ruleTree = self.get_rule_version_node_list(rule_version)
        self.enabledVins = self.get_enabled_vins(rule_version)
        self.dateCreated = rule_version.date_created
        self.dateModified = rule_version.date_modified
        self.state = rule_version.state
        self.text = rule_version.text
        self.specificTest = rule_version.specific_test
        self.testCategory = rule_version.test_category
        self.testType = rule_version.test_type
        self.notes = self.get_rule_version_note_list(rule_version)
        self.lock['isLocked'] = rule_version.is_locked
        self.lock['lockedByUserId'] = rule_version.locked_by_user_id

    def get_rule_version_node_list(self, rule_version):
        """
        get associated rule version node list
        :param rule_version: rule version
        :return: rule version node list
        """
        results = []
        rule_version_nodes = RuleVersionNode.objects.filter(rule_version=rule_version)

        for rule_version_node in list(rule_version_nodes):
            results.append(RuleVersionNodeSerializer(rule_version_node).to_dict())

        return results

    def get_rule_version_note_list(self, rule_version):
        """
        get associated rule version note list
        :param rule_version: rule version
        :return: rule version note list
        """
        results = []
        rule_version_notes = RuleVersionNote.objects.filter(rule_version=rule_version)

        for rule_version_note in list(rule_version_notes):
            results.append(RuleVersionNoteSerializer(rule_version_note).to_dict())

        return results

    def get_enabled_vins(self, rule_version):
        """
        get enabled vins
        :param rule_version: rule version
        :return: vin list
        """
        results = []
        vin_ids = []
        rule_version_has_vins = RuleVersionHasVin.objects.filter(rule_version=rule_version)

        for rule_version_has_vin in list(rule_version_has_vins):
            vin_ids.append(rule_version_has_vin.vins.id)

        vins = Vin.objects.filter(id__in=vin_ids)

        for vin in list(vins):
            results.append(VinSerializer(vin).to_dict())

        return results
