import jwt
from rest_framework.views import APIView
from app.exceptions.http import HttpException
from app.config import Config
from app.service.user import UserService


class BaseAPI(APIView):
    def check_user_token(self, request, only_admin=False):
        """
        check token validation
        :param request: request
        :param only_admin: accept only admin
        :return: current user as dictionary
        """
        token = request.headers.get('Authorization')

        if token is None:
            raise HttpException(401, 'Token is missing')

        token = token.replace('Bearer ', '')

        # decode token
        try:
            current_user = jwt.decode(token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
        except jwt.exceptions.InvalidTokenError:
            raise HttpException(401, 'Invalid user token')

        # check user exists
        if not UserService().check_user_exists(current_user.get('id')):
            raise HttpException(404, 'User not exists')

        # check admin
        if only_admin and current_user.get('role') != 'admin':
            raise HttpException(403, 'Only Admin users are allowed')

        return current_user
