from app.exceptions.http import HttpException
from app.serializers.user import UserSerializer
from app.serializers.query import QuerySerializer
from app.serializers.paging import PagingSerializer
from app.utils import helper
from app.models import User


class UserService:
    """
    user service

    get_user(): get user
    check_user_exists(): get user exists boolean
    delete_user(): delete user
    update_user_role(): update user role
    get_user_list(): get user list
    get_user_total(): get user total count
    search_user(): search user with filter
    """
    def get_user(self, id):
        """
        get user
        :param id: user id
        :return: user
        """
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise HttpException(404, 'User not found')

    def check_user_exists(self, id):
        """
        check user exists
        :param id: user id
        :return: boolean
        """
        exists = True

        try:
            self.get_user(id)
        except HttpException:
            exists = False

        return exists

    def delete_user(self, id):
        """
        delete user
        :param id: user id
        :return: void
        """
        user = self.get_user(id)
        user.delete()

    def update_user_role(self, id, data):
        """
        update user role
        :param id: user id
        :param data: data
        :return: void
        """
        # get user
        user = self.get_user(id)

        if data is None:
            raise HttpException(400, 'no payload')

        # check role validation
        role = data.get('newRole')

        if role is None or role not in ['standard', 'admin']:
            raise HttpException(400, 'newRole should be \'standard\' or \'admin\', current: ' + role)

        # update user
        user.role = role
        user.save()

    def get_user_list(self, offset, limit, sort_by):
        """
        get user list by options
        :param offset: offset
        :param limit: limit
        :param sort_by: sort by
        :return: user list
        """
        results = list()
        users = User.objects.order_by(sort_by)[offset:offset + limit]

        for user in list(users):
            results.append(UserSerializer(user).to_dict())

        return results

    def get_user_total(self):
        """
        get user total count
        :return: count
        """
        return User.objects.count()

    def search_user(self, query):
        """
        search user
        :param query: query
        :return: paging dictionary
        """
        # get queries
        query = QuerySerializer(query)

        limit = query.get('limit', 10000000000, 'int')
        offset = query.get('offset', 0, 'int')
        sort_by = query.get('sortBy', 'name')
        sort_order = query.get('sortOrder', 'asc')

        # check sort by value
        helper.check_choices('sortBy', sort_by, ['name', 'email', 'role'])
        helper.check_choices('sortOrder', sort_order, ['asc', 'desc'])

        # set desc sort by
        if sort_order == 'desc':
            sort_by = '-' + sort_by

        # get users
        users = self.get_user_list(offset, limit, sort_by)

        # get total
        total = self.get_user_total()

        # return
        return PagingSerializer(offset, limit, total, users).to_dict()