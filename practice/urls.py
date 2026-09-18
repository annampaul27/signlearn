from django.urls import path

from . import views

app_name = "practice"

urlpatterns = [
    path("", views.practice_home, name="practice_home"),
    path("answer/", views.submit_practice_answer, name="submit_answer"),
    path("dashboard/", views.practice_dashboard, name="dashboard"),
]