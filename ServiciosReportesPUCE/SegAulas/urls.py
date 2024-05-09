from django.urls import path
from . import views

urlpatterns = [
    path("", views.Inicio, name="InicioTablero"),
    
    path("SeguimientoAulas", views.SeguimientoAulas, name="SeguimientoAulas"),
]
