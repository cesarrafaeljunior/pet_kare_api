from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from rest_framework.views import APIView, Response, Request, status
from pets.models import Pet
from pets.serializer import PetSerializer
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination
import ipdb


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:

        pets = Pet.objects.all()

        pet_params = request.query_params.get("trait", None)

        if pet_params:
            pets_filtereds = pets.filter(traits__name=pet_params)
            result_page = self.paginate_queryset(pets_filtereds, request)

        else:
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
        trait_object = Trait.objects.filter(name__contains=traits_name).first()

        if not trait_object:
            trait_object = Trait.objects.create(name=traits_name)
            traits.append(trait_object)
        traits.append(trait_object)

    pet_instance = Pet.objects.create(**pet.validated_data)

    pet_instance.traits.set(traits)

    return pet_instance


class PetViewId(APIView):
    def get(self, request: Request, pet_id: int) -> Response:

        pet = get_object_or_404(Pet, id=pet_id)

        pet_serializer = PetSerializer(pet)

        return Response(pet_serializer.data)

    def patch(self, request: Request, pet_id: int) -> Response:

        pet = get_object_or_404(Pet, id=pet_id)

        pet_serializer = PetSerializer(data=request.data, partial=True)
        pet_serializer.is_valid(raise_exception=True)

        group_data: dict = pet_serializer.validated_data.pop("group", None)
        traits_data: list = pet_serializer.validated_data.pop("traits", None)

        if group_data:

            group_obj = Group.objects.get(pets=pet.id)

            for key, value in group_data.items():
                setattr(group_obj, key, value)

            group_obj = Group.objects.filter(scientific_name__contains=group_data["scientific_name"]).first()

            if not group_obj:
                group_obj = Group.objects.create(**group_data)
                pet_serializer.validated_data["group"] = group_obj

            pet_serializer.validated_data["group"] = group_obj
            pet.group = pet_serializer.validated_data["group"]

        if traits_data:

            for traits in traits_data:
                try:
                    trait_obj = Trait.objects.get(name__contains=traits["name"])
                    pet.traits.add(trait_obj)
                except Trait.DoesNotExist:
                    trait_obj = Trait.objects.create(**traits)
                    trait_obj.save()
                    pet.traits.add(trait_obj)

        for key, value in pet_serializer.validated_data.items():
            setattr(pet, key, value)
        pet.save()

        pet_serializer = PetSerializer(pet)

        return Response(pet_serializer.data)

    def delete(self, request: Request, pet_id: int) -> Response:

        pet_delete = get_object_or_404(Pet, id=pet_id)

        pet_delete.delete()

        return Response(None, status.HTTP_204_NO_CONTENT)
