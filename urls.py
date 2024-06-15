from django.urls import path
from . import views

urlpatterns = [
    path("SeguimientoAulas", views.SeguimientoAulas, name="SeguimientoAulas"),
    path("GenerarReportesSeguimiento", views.GenerarReportesSeguimiento, name="GenerarReportesSeguimiento"),
    path("DescargarReporte/<int:identificador_proceso>", views.DescargarReporteSeguimientoAulas, name="DescargarReporteSeguimientoAulas"),
]
