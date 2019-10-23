from app.serializers.base import BaseSerializer


class RuleVersionNodeSerializer(BaseSerializer):
    """
    rule version node serializer
    """
    id = 0
    parentId = 0
    text = None

    def __init__(self, rule_version_node):
        self.id = rule_version_node.node_id
        self.parentId = rule_version_node.parent_id
        self.text = rule_version_node.rule_text
