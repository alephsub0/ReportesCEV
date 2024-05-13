from django.urls import path
from . import views

urlpatterns = [
    path("SeguimientoAulas", views.SeguimientoAulas, name="SeguimientoAulas"),
]
