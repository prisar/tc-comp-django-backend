class RuleFunctionSerializer():
    """
    rule function serializer
    """
    nextTokens = None
    translation = None
    parses = None
    isComplete = None

    def __init__(self, next_tokens=None, translation=None, parses=None, is_complete=None):
        self.nextTokens = next_tokens
        self.translation = translation
        self.parses = parses
        self.isComplete = is_complete

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
            if getattr(self, field) is not None:
                dic[field] = getattr(self, field)

        return dic
