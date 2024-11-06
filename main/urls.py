from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
    path("scenario/", views.scenario_view, name="scenario_view"),
    path("select_recommendation/<int:scenario_id>/", views.select_recommendation, name="select_recommendation"),
]