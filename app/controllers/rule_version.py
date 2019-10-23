from rest_framework.response import Response
from rest_framework import status
from app.serializers.rule_version import RuleVersionSerializer
from app.serializers.status import StatusSerializer
from app.exceptions.http import HttpException
from app.controllers.base import BaseAPI
from app.service.rule import RuleVersionService
from app.utils import helper


class RuleVersionDetailAPI(BaseAPI):
    """
    rule version detail api

    get(): get single rule
    delete(): delete single rule
    patch(): update ruleTree, enabledVins, specificTest, testCategory, testType
    """
    def get(self, request, id):
        """
        get rule version by id
        :param request: request
        :param id: rule version id
        :return: response
        """
        try:
            # check id parameter and user token
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            rule_version = RuleVersionService().get_rule_version(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            RuleVersionSerializer(rule_version).to_dict(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id):
        """
        delete rule version
        only admin can delete
        :param request: request
        :param id: rule version id
        :return: response
        """
        try:
            # check id parameter and user token - only admin
            helper.check_int('id parameter', id)
            self.check_user_token(request, True)

            RuleVersionService().delete_rule_version(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, id):
        """
        patch rule version
        :param request: request
        :param id: rule version id
        :return: response
        """
        try:
            # check id and user token
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            RuleVersionService().patch_rule_version(id, current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class RuleVersionListAPI(BaseAPI):
    """
    rule version list api

    get(): get rule version list pagination
    post(): create new rule version
    """
    def get(self, request, id):
        """
        get rule versions
        :param request: request
        :param id: rule id
        :return: response
        """
        # check id parameter and user token
        try:
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            paging_dict = RuleVersionService().search_rule_versions(id, request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            paging_dict,
            status=status.HTTP_200_OK,
        )

    def post(self, request, id):
        """
        create new rule version
        :param request: request
        :param id: rule id
        :return: response
        """
        try:
            # check id parameter and user token
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            created_rule_version = RuleVersionService().create_new_rule_version(
                id,
                current_user,
                request.data,
            )
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            RuleVersionSerializer(created_rule_version).to_dict(),
            status=status.HTTP_201_CREATED,
        )


class RuleVersionModifyAPI(RuleVersionDetailAPI):
    """
    rule version modify api

    put(): modify state, text, locked state
    post(): create new note
    """
    def put(self, request, id, modify_type):
        """
        update rule versions
        :param request: request
        :param modify_type: modify type
        :return: response
        """
        try:
            # check id validation and user token
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # modify
            RuleVersionService().modify_rule_version(id, current_user, modify_type, request.data)

            # success
            return Response(status=status.HTTP_204_NO_CONTENT)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

    def post(self, request, id, modify_type):
        """
        update rule version
        :param request: request
        :param id: rule version id
        :param modify_type: modify type
        :return: response
        """
        try:
            # check id validation and user token
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # create new note
            RuleVersionService().create_new_notes(current_user, modify_type, id, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)
