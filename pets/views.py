from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework.views import APIView, Response, Request, status
from pets.models import Pet
from pets.serializer import PetSerializer
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request)

        pets_serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(pets_serializer.data)

    def post(self, request: Request) -> Response:
        pet_infos = request.data
        pet_serializer = PetSerializer(data=pet_infos)

        pet_serializer.is_valid(raise_exception=True)

        pet = fields_validate(pet_serializer)

        pet_serializer = PetSerializer(pet)

        return Response(pet_serializer.data, status.HTTP_201_CREATED)


def fields_validate(pet):
    traits_data_list = pet.validated_data.pop("traits")

    group_name = pet.validated_data["group"]["scientific_name"]

    group_object = Group.objects.filter(scientific_name__icontains=group_name).first()

    if not group_object:
        group_object = Group.objects.create(scientific_name=group_name)

    pet.validated_data["group"] = group_object

    traits = []
    for traits_dicts in traits_data_list:
        traits_name = traits_dicts["name"]
        trait_object = Trait.objects.filter(name__icontains=traits_name).first()

        if not trait_object:
            trait_object = Trait.objects.create(name=traits_name)
            traits.append(trait_object)
        traits.append(trait_object)

    pet_instance = Pet.objects.create(**pet.validated_data)

    pet_instance.traits.set(traits)

    return pet_instance
