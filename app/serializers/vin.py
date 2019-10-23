from app.serializers.base import BaseSerializer


class VinSerializer(BaseSerializer):
    """
    vin serializer
    """
    id = 0
    vin = None

    def __init__(self, vin):
        self.id = vin.id
        self.vin = vin.name
