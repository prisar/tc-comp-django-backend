from rest_framework.response import Response
from rest_framework import status
from app.serializers.rule import RuleSerializer
from app.serializers.status import StatusSerializer
from app.exceptions.http import HttpException
from app.controllers.base import BaseAPI
from app.utils import helper
from app.service.rule import RuleService


class RuleDetailAPI(BaseAPI):
    """
    rule detail api

    get(): get single rule
    delete(): delete single rule
    patch(): update single rule
    """
    def get(self, request, id):
        """
        get rule by id
        :param request: request
        :param id: rule id
        :return: response
        """
        # check id parameter and user token
        try:
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            # get rule
            rule = RuleService().get_rule(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            RuleSerializer(rule).to_dict(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id):
        """
        delete rule
        :param request: request
        :param id: rule id
        :return: response
        """
        try:
            # check id parameter and user token
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            # delete rule
            RuleService().delete_rule(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, id):
        """
        patch rule
        :param request: request
        :param id: rule id
        :return: response
        """
        try:
            # check id parameter and user token
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            # patch
            RuleService().update_rule(id, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

class RuleListAPI(BaseAPI):
    """
    rule list api

    get(): get rule list pagination
    post(): create new rule
    """
    def get(self, request):
        """
        get rule list
        :param request: request
        :return: response
        """
        try:
            # check validation and get current user dictionary
            self.check_user_token(request)

            # search rules
            paging_dict = RuleService().search_rules(request.query_params)
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

    def post(self, request):
        """
        create new rule
        :param request: request
        :return: response
        """
        try:
            # check validation and get current user dictionary
            self.check_user_token(request)

            # create new rule
            created_rule = RuleService().create_new_rule(request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            RuleSerializer(created_rule).to_dict(),
            status=status.HTTP_201_CREATED,
        )


class RuleCopyAPI(BaseAPI):
    """
    rule copy api

    post(): copy existing rule
    """
    def post(self, request, id):
        """
        copy rule
        :param request: request
        :param id: rule id
        :return: response
        """
        try:
            # check id and parameters
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # copy
            copied_rule = RuleService().copy_rule(current_user, id, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            RuleSerializer(copied_rule).to_dict(),
            status=status.HTTP_201_CREATED,
        )
