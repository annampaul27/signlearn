from django.urls import path
from . import views

urlpatterns = [
    path("alphabet/", views.alphabet, name="alphabet"),

    path(
        "alphabet/<int:sign_id>/",
        views.sign_detail,
        name="sign_detail"
    ),
]