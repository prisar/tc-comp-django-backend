from rest_framework.response import Response
from rest_framework import status
from app.serializers.status import StatusSerializer
from app.exceptions.http import HttpException
from app.controllers.base import BaseAPI
from app.service.rule_function import RuleFunctionService


class RuleFunctionAPI(BaseAPI):
    """
    rule function controller

    post(): parse rule text according to function
    get(): get specific test
    """
    def post(self, request, function):
        """
        parse rule text
        :param request: request
        :param function: parse function
        :return: Response
        """
        try:
            # check user token
            self.check_user_token(request)

            # parse rule text
            result = RuleFunctionService().parse_rule_text(request.data, function)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            result.to_dict(),
            status=status.HTTP_200_OK,
        )

    def get(self, request, function):
        """
        get specific test
        :param request: request
        :param function: function
        :return: Response
        """
        try:
            # check user token
            self.check_user_token(request)

            # get test by category
            result = RuleFunctionService().get_test_by_category(request.query_params, function)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            result,
            status=status.HTTP_200_OK,
        )

