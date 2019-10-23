class BaseSerializer:
    """
    base serializer
    """
    def to_dict(self):
        """
        change class to dictionary
        :return: dictionary
        """
        dic = {}
        fields = [
            attr for attr in dir(self) if not hasattr(getattr(self, attr), '__call__') and not attr.startswith('__')
        ]

        for field in fields:
            dic[field] = getattr(self, field)

        return dic
