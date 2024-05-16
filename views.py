from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .forms import FormularioSeguimientoAulas
import pandas as pd
from .funciones import procesar_seguimiento
from .models import ModeloSeguimientoAulas
from ServiciosReportesPUCE.settings import MEDIA_ROOT
import os
from django.contrib import messages

def is_member_puce(user):
    return user.groups.filter(name="PUCE_Basico").exists()


def generar_codigo():
    """
    Genera un código único con la fecha y hora actual.

    Returns:
        str: Código único con la fecha y hora actual.
    """
    return pd.Timestamp.now().strftime("%Y%m%d%H%M%S")


def elaborar_reportes(identificador_proceso, nombre_coordinador):
    # Obtenemos la ruta del archivo excel
    archivo = ModeloSeguimientoAulas.objects.get(
        IdProceso=identificador_proceso
    ).ArchivoSeguimiento

    # Generamos la ruta al archivo excel
    ruta_archivo = os.path.join(MEDIA_ROOT, str(archivo))

    # Generamos los reportes
    ruta_comprimido = procesar_seguimiento(ruta_archivo, nombre_coordinador,identificador_proceso)

    # Guardamos la ruta en el modelo con el identificador del proceso
    ModeloSeguimientoAulas.objects.filter(
        IdProceso=identificador_proceso
    ).update(ArchivoComprimido=ruta_comprimido)

@user_passes_test(is_member_puce)
@login_required
def GenerarReportesSeguimiento(request):
    if request.method == "POST":
        form = FormularioSeguimientoAulas(request.POST, request.FILES)
        if form.is_valid():

            identificador_proceso = generar_codigo()

            # Agregamos el código del proceso al formulario
            form.instance.IdProceso = identificador_proceso
            form.instance.IdUsuario = request.user.id

            # Guardamos el formulario
            form.save()

            # Obtenemos el nombre del coordinador
            nombre_coordinador = form.cleaned_data["NombreCoordinador"]

            elaborar_reportes(
                identificador_proceso, nombre_coordinador
            )

            json_respuesta = {
                "status": "success",
                "code" : identificador_proceso
            }

            return JsonResponse(json_respuesta, safe=False)

@user_passes_test(is_member_puce)
@login_required
def SeguimientoAulas(request):
    if request.method == "GET":

        formulario = FormularioSeguimientoAulas()
        return render(request, "SeguimientoAulas.html", {"formulario": formulario})

@user_passes_test(is_member_puce)
@login_required
def DescargarReporteSeguimientoAulas(request, identificador_proceso):
    if request.method == "GET":

        # Verificamos si el usuario que solicita la descarga es el mismo que generó el proceso
        UsuarioProceso = ModeloSeguimientoAulas.objects.get(
            IdProceso=identificador_proceso
        ).IdUsuario

        if request.user.id != UsuarioProceso:
            messages.error(request, "No tienes permiso para descargar este archivo")
            return render (request, "SeguimientoAulas.html")


        # Obtenemos la ruta del archivo comprimido
        archivo_comprimido = ModeloSeguimientoAulas.objects.get(
            IdProceso=identificador_proceso
        ).ArchivoComprimido

        # Generamos la ruta al archivo comprimido
        ruta_archivo = os.path.join(MEDIA_ROOT, str(archivo_comprimido))

        # Leemos el archivo
        with open(ruta_archivo, "rb") as archivo:
            contenido = archivo.read()

        # Generamos la respuesta
        response = HttpResponse(contenido, content_type="application/zip")
        response["Content-Disposition"] = f"attachment; filename={archivo_comprimido}"

        return response