from django.urls import path

from . import views

app_name = "adminpanel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("signs/", views.sign_list, name="sign_list"),
    path("signs/add/", views.sign_create, name="sign_create"),
    path("signs/<int:sign_id>/edit/", views.sign_edit, name="sign_edit"),
    path("signs/<int:sign_id>/delete/", views.sign_delete, name="sign_delete"),

    path("tests/", views.test_list, name="test_list"),
    path("tests/add/", views.test_create, name="test_create"),
    path("tests/<int:test_id>/edit/", views.test_edit, name="test_edit"),
    path("tests/<int:test_id>/delete/", views.test_delete, name="test_delete"),

    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.user_create, name="user_create"),
    path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:user_id>/delete/", views.user_delete, name="user_delete"),

    path("settings/", views.settings_edit, name="settings_edit"),
]
