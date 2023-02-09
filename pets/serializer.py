from rest_framework import serializers
from traits.serializer import TraitSerializer
from groups.serializer import GroupSerializer
from pets.models import SexOptions


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices=SexOptions.choices,
        default=SexOptions.DEFAULT)
    group = GroupSerializer()
    traits = TraitSerializer(many=True)
