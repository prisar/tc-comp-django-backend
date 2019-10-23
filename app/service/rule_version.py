from django.db import transaction, IntegrityError
from app.models import RuleVersionNote, RuleVersionHasVin, RuleVersionNode, RuleVersion, Vin, Rule
from app.exceptions.http import HttpException
from app.utils import helper
from app.serializers.rule_version import RuleVersionSerializer
from app.serializers.query import QuerySerializer
from app.serializers.paging import PagingSerializer
from app.service.user import UserService


class RuleVersionService:
    """
    rule version service

    get_rule(): get single rule
    get_rule_version(): get single rule version
    delete_rule_version(): delete single rule version with associates
    patch_rule_version(): update fields of the rule version
    validate_rule_trees(): validate rule tree field
    validate_enabled_vins(): validate enabled vins field
    delete_and_insert_rule_version_nodes(): delete existing and insert new rule version nodes
    update_or_insert_vins(): update, insert or delete vins and rule_version_has_vins
    get_rule_version_list(): get rule version list
    get_rule_versions_total(): get rule version total count
    search_rule_versions(): search rule versions with pagination
    create_new_rule_version(): create new rule version
    modify_rule_version(): modify rule version
    reject_publish(): set state to Draft
    approve_publish(): set state to Published
    request_publish(): set state to In Review
    lock_unlock_rule_version(): lock or unlock rule version
    modify_text(): modify rule version text field
    create_new_notes(): create new notes for rule version
    copy_rule_version(): copy rule version with associates
    copy_rule_version_has_vins(): copy rule version has vins
    copy_rule_version_notes(): copy rule version notes
    copy_rule_version_nodes(): copy rule version nodes
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

    def get_rule_version(self, id):
        """
        check rule version exists
        :param id: rule version id
        :return: rule version
        """
        try:
            return RuleVersion.objects.get(id=id)
        except RuleVersion.DoesNotExist:
            raise HttpException(404, 'Rule version not found')

    def delete_rule_version(self, id):
        """
        delete rule version
        :param id: rule version id
        :return: void
        """
        # get rule version
        rule_version = self.get_rule_version(id)

        # invalid state
        if rule_version.state == 'Published':
            raise HttpException(403, 'Rule version cannot be modified or deleted in \'Published\' state')

        # get associated
        rule_version_nodes = RuleVersionNode.objects.filter(rule_version=rule_version)
        rule_version_notes = RuleVersionNote.objects.filter(rule_version=rule_version)
        rule_version_has_vins = RuleVersionHasVin.objects.filter(rule_version=rule_version)

        # delete
        with transaction.atomic():
            rule_version_has_vins.delete()
            rule_version_notes.delete()
            rule_version_nodes.delete()
            rule_version.delete()

    def patch_rule_version(self, id, user_dict, data):
        """
        patch rule version
        :param id: rule version id
        :param user_dict: user dictionary
        :param data: request data
        :return: void
        """
        # get rule version
        rule_version = self.get_rule_version(id)

        # invalid state
        if rule_version.state != 'Draft':
            raise HttpException(403, 'Rule version state is not \'Draft\': ' + rule_version.state)

        # when locked, restricted to locked user only
        if rule_version.is_locked and rule_version.locked_by_user_id != user_dict.get('id'):
            raise HttpException(403, 'Only the user who locked can be allowed to modify locked rule version')

        # get request data
        rule_trees = data.get('ruleTree')
        enabled_vins = data.get('enabledVins')

        # check validations
        if rule_trees is not None:
            helper.check_array('ruleTree', rule_trees)
            self.validate_rule_trees(rule_trees)

        if enabled_vins is not None:
            helper.check_array('enabledVins', enabled_vins)
            self.validate_enabled_vins(enabled_vins)

        # set value for update
        rule_version.specific_test = helper.get_default_string(data.get('specificTest'), rule_version.specific_test)
        rule_version.test_category = helper.get_default_string(data.get('testCategory'), rule_version.test_category)
        rule_version.test_type = helper.get_default_string(data.get('testType'), rule_version.test_type)

        # get existing rule trees
        rule_version_nodes = RuleVersionNode.objects.filter(rule_version=rule_version)

        with transaction.atomic():
            # delete and insert rule version nodes
            if rule_trees is not None:
                self.delete_and_insert_rule_version_nodes(rule_version_nodes, rule_version, rule_trees)

            # update and insert new vins and rule version has vins
            if enabled_vins is not None:
                self.update_or_insert_vins(rule_version, enabled_vins)

            rule_version.save()

    def validate_rule_trees(self, rule_trees):
        """
        validate rule trees
        :param rule_trees: rule trees
        :return: void
        """
        # true when rule trees is none or empty list
        if rule_trees is None or len(rule_trees) == 0:
            return True

        # check validation
        root_exists = False

        for rule_tree in rule_trees:
            if rule_tree.get('parentId') is None:
                root_exists = True

            if type(rule_tree.get('id')) is not int or rule_tree.get('id') == 0:
                raise HttpException(400, 'Rule tree id field must be an integer, not null and zero')

            if type(rule_tree.get('parentId')) is not int and rule_tree.get('parentId') is not None:
                raise HttpException(400, 'Rule tree parentId field must be a null or an integer')

            if type(rule_tree.get('text')) is not str:
                raise HttpException(400, 'Rule tree text field must be a string, not null')

        if not root_exists:
            raise HttpException(400, 'Rule tree does not have root node')

    def validate_enabled_vins(self, enabled_vins):
        """
        validate enabled vins
        :param enabled_vins: enabled vins
        :return: void
        """
        # true when enabled vins is none or empty list
        if enabled_vins is None or len(enabled_vins) == 0:
            return True

        for enabled_vin in enabled_vins:
            if enabled_vin.get('id') is not None and (type(enabled_vin.get('id')) is not int or enabled_vin.get('id') == 0):
                raise HttpException(400, 'Enabled vin id field must be an integer or null')

            if type(enabled_vin.get('vin')) is not str:
                raise HttpException(400, 'Enabled vin vin field must be a string, not null')

    def delete_and_insert_rule_version_nodes(self, rule_version_nodes, rule_version, rule_trees):
        """
        delete existing rule version nodes and insert new rule version nodes
        :param rule_version_nodes: existing rule version nodes
        :param rule_version: rule version
        :param rule_trees: rule trees data
        :return: void
        """
        # remove existing rule version nodes
        rule_version_nodes.delete()

        # insert rule version node
        for rule_tree in rule_trees:
            RuleVersionNode.objects.create(
                node_id=rule_tree.get('id'),
                rule_text=rule_tree.get('text'),
                rule_version=rule_version,
                parent_id=rule_tree.get('parentId'),
            )

    def update_or_insert_vins(self, rule_version, enabled_vins):
        """
        update or insert new vins and rule version has vins
        :param rule_version: rule version
        :param enabled_vins: enabled vins data
        :return: void
        """
        # get rule version has vin ids
        vin_ids = []
        rule_version_has_vins = RuleVersionHasVin.objects.filter(rule_version=rule_version)

        for rule_version_has_vin in list(rule_version_has_vins):
            vin_ids.append(rule_version_has_vin.id)

        # insert or update rule version has vins and vins
        processed_vin_ids = []

        for enabled_vin in enabled_vins:
            if enabled_vin.get('id') is not None and enabled_vin.get('id') in vin_ids:
                # update vin
                vin = Vin.objects.get(id=enabled_vin.get('id'))
                vin.name = enabled_vin.get('vin')
                vin.save()

                # append processed vin ids
                processed_vin_ids.append(enabled_vin.get('id'))

            else:
                # create vin and rule version has vin
                created_vin = Vin.objects.create(name=enabled_vin.get('vin'))
                RuleVersionHasVin.objects.create(rule_version=rule_version, vins=created_vin)

                # append processed vin ids
                processed_vin_ids.append(created_vin.id)

        # remove unprocessed vins and rule version has vins
        unprocessed_vins = Vin.objects.exclude(id__in=processed_vin_ids)
        RuleVersionHasVin.objects.filter(vins__in=unprocessed_vins).delete()

    def get_rule_version_list(self, offset, limit, id):
        """
        get rule version list
        :param offset: offset
        :param limit: limit
        :param id: rule id
        :return: rule list
        """
        results = list()
        rule = self.get_rule(id)
        rule_versions = RuleVersion.objects.filter(rule=rule)[offset:offset + limit]

        for rule_version in list(rule_versions):
            results.append(RuleVersionSerializer(rule_version).to_dict())

        return results

    def get_rule_versions_total(self, id):
        """
        get rule version total count
        :param id: rule id
        :return: total count
        """
        rule = self.get_rule(id)

        return RuleVersion.objects.filter(rule=rule).count()

    def search_rule_versions(self, id, query):
        """
        search rule versions
        :param id: rule id
        :param query: query
        :return: paging dictionary
        """
        # get query
        query = QuerySerializer(query)

        # validate query params
        offset = query.get('offset', 0, 'int')
        limit = query.get('limit', 10000000000, 'int')

        # get rule version list
        rule_version_list = self.get_rule_version_list(offset, limit, id)
        total = self.get_rule_versions_total(id)

        return PagingSerializer(offset, limit, total, rule_version_list).to_dict()

    def create_new_rule_version(self, id, user_dict, data):
        """
        create new rule version
        :param id: rule id
        :param user_dict: user dictionary
        :param data: data
        :return: created rule version
        """
        notes = data.get('notes')
        version_number = data.get('versionNumber');
        user = UserService().get_user(user_dict.get('id'))

        # check version_number validation
        if version_number is None or version_number == '':
            raise HttpException(400, 'Invalid rule version number')

        # check notes validation
        if notes is not None and notes == '':
            raise HttpException(400, 'Invalid rule notes')

        # get rule
        rule = self.get_rule(id)

        # create rule version and notes
        try:
            with transaction.atomic():
                # create rule version
                created_rule_version = RuleVersion.objects.create(
                    version_number=version_number,
                    user=user,
                    state='Draft',
                    rule=rule,
                )

                # create note
                RuleVersionNote.objects.create(user=user, notes=notes, rule_version=created_rule_version)
        except IntegrityError:
            raise HttpException(409, 'Version ' + version_number + ' on rule id ' + str(id) + ' already exists')

        # return
        return created_rule_version

    def modify_rule_version(self, id,  user_dict, modify_type, data):
        """
        modify rule version
        :param id: rule version id
        :param user_dict: user dictionary
        :param modify_type: modify type
        :param data: data
        :return: void
        """
        # reject publish
        if modify_type == 'reject':
            self.reject_publish(user_dict, id)

        # approve publish
        elif modify_type == 'approve':
            self.approve_publish(user_dict, id)

        # request publish
        elif modify_type == 'publish':
            self.request_publish(id)

        # lock or unlock
        elif modify_type == 'lock':
            lock_state = data.get('newIsLocked')

            self.lock_unlock_rule_version(user_dict, lock_state, id)

        # modify text
        elif modify_type == 'text':
            text = data.get('newText')

            self.modify_text(user_dict, text, id)

        else:
            raise HttpException(404, 'Endpoint not found: ' + modify_type)

    def reject_publish(self, user, id):
        """
        reject publish
        :param user: current user
        :param id: rule version id
        :return: void
        """
        # invalid user
        if user.get('role') != 'admin':
            raise HttpException(403, 'Only Admin users are allowed')

        rule_version = self.get_rule_version(id)

        # invalid state
        if rule_version.state != 'In Review':
            raise HttpException(403, 'Rule version state is not \'In Review\': ' + rule_version.state)

        rule_version.state = 'Draft'
        rule_version.save()

    def approve_publish(self, user, id):
        """
        approve publish
        :param user: current user
        :param id: rule version id
        :return: void
        """
        # invalid user
        if user.get('role') != 'admin':
            raise HttpException(403, 'Only Admin users are allowed')

        rule_version = self.get_rule_version(id)

        # invalid state
        if rule_version.state != 'In Review':
            raise HttpException(403, 'Rule version state is not \'In Review\': ' + rule_version.state)

        rule_version.state = 'Published'
        rule_version.save()

    def request_publish(self, id):
        """
        request to publish
        :param id: rule version id
        :return: void
        """
        rule_version = self.get_rule_version(id)

        # invalid state
        if rule_version.state != 'Draft':
            raise HttpException(403, 'Rule version state is not \'Draft\': ' + rule_version.state)

        rule_version.state = 'In Review'
        rule_version.save()

    def lock_unlock_rule_version(self, user, lock_state, id):
        """
        lock or unlock rule version
        :param user: current user
        :param lock_state: lock state
        :param id: rule version id
        :return: void
        """
        # invalid lock state
        if lock_state not in [True, False]:
            raise HttpException(403, 'Invalid newIsLocked value')

        rule_version = self.get_rule_version(id)

        # invalid state
        if rule_version.state != 'Draft':
            raise HttpException(403, 'Rule version state is not \'Draft\': ' + rule_version.state)

        if lock_state:
            # check locked state
            if rule_version.is_locked:
                raise HttpException(403, 'Rule version already locked')

            # unlock rule version
            rule_version.is_locked = True
            rule_version.locked_by_user_id = user.get('id')
        else:
            # invalid user
            if user.get('role') != 'admin' and rule_version.user.id != user.get('id'):
                raise HttpException(403, 'Only Admin or user who locked are allowed')

            # lock rule version
            rule_version.is_locked = False
            rule_version.locked_by_user_id = 0

        rule_version.save()

    def modify_text(self, user_dict, text, id):
        """
        modify rule version text
        :param text: text
        :param id: rule version id
        :return: void
        """
        # invalid text
        if text is None or text == '':
            raise HttpException(400, 'Invalid text value')

        rule_version = self.get_rule_version(id)

        # invalid state
        if rule_version.state != 'Draft':
            raise HttpException(403, 'Rule version state is not \'Draft\': ' + rule_version.state)

        # when locked, restricted to locked user only
        if rule_version.is_locked and rule_version.locked_by_user_id != user_dict.get('id'):
            raise HttpException(403, 'Only the user who locked can be allowed to modify locked rule version')

        rule_version.text = text
        rule_version.save()

    def create_new_notes(self, user_dict, modify_type, id, data):
        """
        create new note
        :param user_dict: user dictionary
        :param data: data
        :return: void
        """
        # not found
        if modify_type != 'notes':
            raise HttpException(404, 'Endpoint not found: ' + modify_type)

        # get rule_version
        rule_version = self.get_rule_version(id)
        
        # invalid state
        if rule_version.state != 'Draft':
            raise HttpException(403, 'Rule version state is not \'Draft\': ' + rule_version.state)

        # when locked, restricted to locked user only
        if rule_version.is_locked and rule_version.locked_by_user_id != user_dict.get('id'):
            raise HttpException(403, 'Only the user who locked can be allowed to modify locked rule version')

        # get data
        notes = data.get('newNotes')
        user = UserService().get_user(user_dict.get('id'))

        # invalid notes
        if notes is None or notes == '':
            raise HttpException(400, 'Invalid newText value')

        # invalid state
        if rule_version.state != 'Draft':
            raise HttpException(403, 'Rule version state is not \'Draft\': ' + rule_version.state)

        with transaction.atomic():
            # create rule version note and update rule version modified date
            RuleVersionNote.objects.create(notes=notes, user=user, rule_version=rule_version)
            rule_version.save()

    def copy_rule_version(self, id, rule, user):
        """
        copy rule version
        :param id: rule version id
        :param rule: rule
        :param user: user
        :return: copied rule_version
        """
        rule_version = self.get_rule_version(id)

        created_rule_version = RuleVersion.objects.create(
            rule=rule,
            version_number=rule_version.version_number,
            user=user,
            state=rule_version.state,
            text=rule_version.text,
            specific_test=rule_version.specific_test,
            test_category=rule_version.test_category,
            test_type=rule_version.test_type,
            is_locked=rule_version.is_locked,
            locked_by_user_id=rule_version.locked_by_user_id,
        )

        self.copy_rule_version_has_vins(rule_version, created_rule_version)
        self.copy_rule_version_notes(rule_version, created_rule_version)
        self.copy_rule_version_nodes(rule_version, created_rule_version)

    def copy_rule_version_has_vins(self, existing_rule_version, created_rule_version):
        """
        copy rule version has vins
        :param existing_rule_version: existing rule version
        :param created_rule_version: created rule version
        :return: void
        """
        rule_version_has_vins = RuleVersionHasVin.objects.filter(rule_version=existing_rule_version)

        for rule_version_has_vins in list(rule_version_has_vins):
            vin = Vin.objects.get(id=rule_version_has_vins.id)

            RuleVersionHasVin.objects.create(
                rule_version=created_rule_version,
                vins=vin,
            )

    def copy_rule_version_notes(self, existing_rule_version, created_rule_version):
        """
        copy rule version notes
        :param existing_rule_version: existing rule version
        :param created_rule_version: created rule version
        :param user: current user
        :return: void
        """
        rule_version_notes = RuleVersionNote.objects.filter(rule_version=existing_rule_version)

        for rule_version_note in list(rule_version_notes):
            RuleVersionNote.objects.create(
                user=rule_version_note.user,
                notes=rule_version_note.notes,
                rule_version=created_rule_version,
            )

    def copy_rule_version_nodes(self, existing_rule_version, created_rule_version):
        """
        copy rule version node
        :param existing_rule_version: existing rule version
        :param created_rule_version: created rule version
        :return: void
        """
        rule_version_nodes = RuleVersionNode.objects.filter(rule_version=existing_rule_version)

        for rule_version_node in list(rule_version_nodes):
            RuleVersionNode.objects.create(
                node_id=rule_version_node.node_id,
                rule_text=rule_version_node.rule_text,
                parent_id=rule_version_node.parent_id,
                rule_version=created_rule_version,
            )