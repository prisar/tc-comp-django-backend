from rest_framework.response import Response
from rest_framework import status
from app.serializers.workspace import WorkspaceSerializer
from app.serializers.status import StatusSerializer
from app.exceptions.http import HttpException
from app.controllers.base import BaseAPI
from app.utils import helper
from app.service.workspace import WorkspaceService


class WorkspaceDetailAPI(BaseAPI):
    """
    workspace detail api

    get(): get single workspace
    delete(): delete single workspace
    patch(): update single workspace
    """
    def get(self, request, id):
        """
        get workspace detail only user is a member
        :param id: workspace id
        :return: response
        """
        try:
            # check user and parameter validation
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # check is member
            WorkspaceService().check_is_member(id, current_user.get('id'))

            # get workspace
            workspace = WorkspaceService().get_workspace(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            WorkspaceSerializer(workspace).to_dict(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id):
        """
        delete workspace
        :param request: request
        :param id: workspace id
        :return: response
        """
        try:
            # check user and parameter validation
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # delete
            WorkspaceService().delete_workspace(id, current_user)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, id):
        """
        update workspace
        :param request: request
        :param id: workspace id
        :return: response
        """
        try:
            # check user and parameter validation
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # update
            WorkspaceService().update_workspace(id, current_user, request.data)
        except HttpException as e:

            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkspaceListAPI(BaseAPI):
    """
    workspace list api

    get(): search workspaces with paging
    post(): create new workspace
    """
    def get(self, request):
        """
        get workspace list
        :param request: request
        :return: response
        """
        try:
            # check user token
            current_user = self.check_user_token(request)

            # search workspaces
            paging_dict = WorkspaceService().search_workspaces(current_user, request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(
            paging_dict,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        create new workspace
        :param request: request
        :return: response
        """
        try:
            # check validation and get current user dictionary
            current_user = self.check_user_token(request)

            # create
            created_workspace = WorkspaceService().create_new_workspace(current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            WorkspaceSerializer(created_workspace).to_dict(),
            status=status.HTTP_201_CREATED,
        )


class WorkspaceCopyAPI(BaseAPI):
    """
    workspace copy api

    post(): copy workspace
    """
    def post(self, request, id):
        """
        copy workspace
        :param request: request
        :param id: workspace id
        :return: response
        """
        try:
            # check user and parameter validation
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # copy
            copied_workspace = WorkspaceService().copy_workspace(id, current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            WorkspaceSerializer(copied_workspace).to_dict(),
            status=status.HTTP_201_CREATED,
        )

