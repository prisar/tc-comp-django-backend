from rest_framework.response import Response
from rest_framework import status
from app.serializers.project import ProjectSerializer
from app.serializers.status import StatusSerializer
from app.exceptions.http import HttpException
from app.controllers.base import BaseAPI
from app.utils import helper
from app.service.project import ProjectService


class ProjectDetailAPI(BaseAPI):
    """
    project detail api

    get(): get single project
    """
    def get(self, request, id):
        """
        get project
        :param request: request
        :param id: project id
        :return: response
        """
        try:
            # check id and user token
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            # get project
            project = ProjectService().get_project(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            ProjectSerializer(project).to_dict(),
            status=status.HTTP_200_OK,
        )


class ProjectListAPI(BaseAPI):
    """
    project list api

    get(): get project list pagination
    """
    def get(self, request):
        """
        get project list
        :param request: request
        :return: response
        """
        try:
            # check user token
            self.check_user_token(request)

            # search project
            paging_dict = ProjectService().search_projects(request.query_params)
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
