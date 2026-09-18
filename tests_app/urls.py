from django.urls import path

from . import views

app_name = "tests_app"

urlpatterns = [
    path("", views.test_list, name="test_list"),
    path("start/<int:test_id>/", views.start_test, name="start_test"),
    path("attempt/<int:attempt_id>/", views.take_test, name="take_test"),
    path("attempt/<int:attempt_id>/answer/", views.submit_answer, name="submit_answer"),
    path("attempt/<int:attempt_id>/result/", views.test_result, name="test_result"),
]
