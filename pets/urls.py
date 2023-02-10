from django.urls import path
from pets.views import PetView, PetViewId

urlpatterns = [
    path("pets/", PetView.as_view()),
    path("pets/<int:pet_id>/", PetViewId.as_view())
]
