from rest_framework.response import Response
from rest_framework import status
from app.serializers.user import UserSerializer
from app.serializers.status import StatusSerializer
from app.exceptions.http import HttpException
from app.controllers.base import BaseAPI
from app.utils import helper
from app.service.user import UserService


class UserDetailAPI(BaseAPI):
    """
    user detail api

    get(): get single user
    delete(): delete single user
    """
    def get(self, request, id):
        """
        get user data
        :param request: request
        :param id: user id
        :return: response
        """
        try:
            # check validations
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            # get user
            user = UserService().get_user(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            UserSerializer(user).to_dict(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id):
        """
        delete user
        :param request: request
        :param id: user id
        :return:
        """
        try:
            # check validations
            helper.check_int('id parameter', id)
            self.check_user_token(request, True)

            # delete user
            UserService().delete_user(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )
        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRoleAPI(UserDetailAPI):
    """
    user role edit api

    put(): update user role
    """
    def put(self, request, id):
        """
        update user role
        :param request: request
        :param id: user id
        :return: response
        """
        try:
            # check validations
            helper.check_int('id parameter', id)
            self.check_user_token(request, True)

            # update
            UserService().update_user_role(id, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserListAPI(BaseAPI):
    """
    user list api

    get(): get user list paginator
    """
    def get(self, request):
        """
        get user list pagination
        :param request: request
        :return: response
        """
        try:
            # check validation
            self.check_user_token(request, True)

            # search user
            paging_dict = UserService().search_user(request.query_params)
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
