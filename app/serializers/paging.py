from app.serializers.base import BaseSerializer


class PagingSerializer(BaseSerializer):
    """
    paging serializer
    """
    results = []
    paginationInfo = {
        'limit': 0,
        'offset': 0,
        'totalCount': 0,
    }

    def __init__(self, offset=0, limit=0, total=0, data=[]):
        self.paginationInfo['offset'] = offset
        self.paginationInfo['limit'] = limit
        self.paginationInfo['totalCount'] = total
        self.results = data
