from app.serializers.rule import RuleSerializer
from django.db import transaction, IntegrityError
from app.models import RuleVersion, Rule, WorkspacesRule
from app.exceptions.http import HttpException
from app.serializers.query import QuerySerializer
from app.serializers.paging import PagingSerializer
from app.service.user import UserService
from app.service.rule_version import RuleVersionService
from app.utils import helper


class RuleService:
    """
    rule service

    get_rule(): return rule object
    delete_rule(): delete rule with rule_service
    get_rule_list(): get rule list
    get_rule_total(): get rule total count
    search_rules(): search rules with query
    create_new_rule(): create new rule
    update_rule(): update rule name
    copy_rule(): copy rule with rule_version
    """
    def get_rule(self, id):
        """
        get rule
        :param id: rule id
        :return: rule
        """
        try:
            return Rule.objects.get(id=id)
        except Rule.DoesNotExist:
            raise HttpException(404, 'Rule not found')

    def delete_rule(self, id):
        """
        delete rule
        :param id: rule id
        :return: void
        """
        # get rule
        rule = self.get_rule(id)

        # get rule versions
        rule_versions = RuleVersion.objects.filter(rule=rule)
        workspace_rules = WorkspacesRule.objects.filter(rule=rule)

        with transaction.atomic():
            # delete workspace rules
            workspace_rules.delete()

            # delete rule versions
            for rule_version in list(rule_versions):
                RuleVersionService().delete_rule_version(rule_version.id)

            # delete rule
            rule.delete()

    def get_rule_list(self, name, offset, limit, order):
        """
        get rule list
        :param name: name filter
        :param offset: offset
        :param limit: limit
        :param order: order direction
        :return: rule list
        """
        sort_by = 'name' if order == 'asc' else '-name'

        results = list()
        rules = Rule.objects.filter(name__icontains=name).order_by(sort_by)[offset:offset + limit]

        for rule in list(rules):
            results.append(RuleSerializer(rule).to_dict())

        return results

    def get_rule_total(self, name):
        """
        get rule total count
        :param name: rule name
        :return: count
        """
        return Rule.objects.filter(name__icontains=name).count()

    def search_rules(self, query):
        """
        search rules
        :param query: query params
        :return: paging dictionary
        """
        # get queries
        query = QuerySerializer(query)

        name = query.get('name', '')
        offset = query.get('offset', 0, 'int')
        limit = query.get('limit', 10000000000, 'int')
        sort_order = query.get('sortOrder', 'asc')

        # check sort order
        helper.check_choices('sortOrder', sort_order, ['asc', 'desc'])

        # get rules
        rules = self.get_rule_list(name, offset, limit, sort_order)

        # success
        return PagingSerializer(offset, limit, Rule.objects.filter(name__icontains=name).count(), rules).to_dict()

    def update_rule(self, id, data):
        """
        update rule
        :param id: rule id
        :param data: data
        :return: void
        """
        # get rule
        rule = self.get_rule(id)

        # get data
        name = helper.get_default_string(data.get('name'), rule.name)

        # check string
        helper.check_string('name', name)

        rule.name = name

        try:
            rule.save()
        except IntegrityError:
            raise HttpException(409, name + ' already exists')

    def create_new_rule(self, data):
        """
        create new rule
        :param data: data
        :return: created rule
        """
        # get name
        name = data.get('name')

        # check name validation
        if name is None or name == '':
            raise HttpException(400, 'Invalid rule name')

        # create rule
        try:
            return Rule.objects.create(name=name)
        except IntegrityError:
            raise HttpException(409, name + ' already exists')

    def copy_rule(self, user_dict, id, data):
        """
        copy rule
        :param user_dict: user dictionary
        :param id: rule id
        :param data: data
        :return: copied rule
        """
        # get data
        rule = self.get_rule(id)
        name = data.get('name')
        user = UserService().get_user(user_dict.get('id'))

        # check name validation
        if name is None or name == '':
            raise HttpException(400, 'Invalid rule name')

        # check name
        helper.check_string('name', name)

        # get rule and versions
        rule_versions = RuleVersion.objects.filter(rule=rule)

        # create and copy relations
        try:
            with transaction.atomic():
                copied_rule = Rule.objects.create(name=name)

                for rule_version in rule_versions:
                    RuleVersionService().copy_rule_version(rule_version.id, copied_rule, user)

            return copied_rule
        except IntegrityError:
            raise HttpException(409, name + ' already exists')
