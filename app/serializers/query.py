from app.exceptions.http import HttpException


class QuerySerializer:
    """
    query parameter serializer
    """
    query = {}

    def __init__(self, query={}):
        self.query = query

    def get(self, field, default='', value_type='string'):
        value = self.query.get(field)

        if value is None or value == '':
            return default
        else:
            try:
                if value_type == 'string':
                    return str(value)
                elif value_type == 'int':
                    return int(value)
                elif value_type == 'float':
                    return float(value)
                else:
                    return value
            except ValueError:
                raise HttpException(400, 'Invalid parameter type, parameter: ' + field)
