# Módulos del script
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import FormularioSeguimientoAulas
import pandas as pd
from .reportes_cev import procesar_seguimiento
from .models import ModeloSeguimientoAulas
from ServiciosReportesPUCE.settings import (
    MEDIA_ROOT,
    DIRECTORIO_TEMPORAL_REPORTES_CEV,
    GRUPOS_SEGURIDAD,
)
import os
from django.contrib import messages
from django.conf import settings
import sys
from ServiciosReportesPUCE.funciones import (
    obtener_usuario_id,
    verificar_miembro_grupo_seguridad,
    informacion_usuario
)

# Variables del script
nombre_grupo_seg = "reportes_cev"

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

    # Cambiamos el directorio de trabajo a la carpeta temporal
    os.chdir(DIRECTORIO_TEMPORAL_REPORTES_CEV)

    # Generamos los reportes
    try:
        procesar_seguimiento(
            ruta_archivo,
            nombre_coordinador,
            DIRECTORIO_TEMPORAL_REPORTES_CEV,
            identificador_proceso,
        )

        # Movemos el archivo comprimido a la carpeta uploads/comprimidos_cev para su descarga
        ruta_comprimido = os.path.join(
            MEDIA_ROOT, "comprimidos_cev", f"Seguimiento-{identificador_proceso}.zip"
        )

        ruta_generado = os.path.join(
            DIRECTORIO_TEMPORAL_REPORTES_CEV, f"Seguimiento-{identificador_proceso}.zip"
        )

        # Movemos el archivo comprimido a la carpeta uploads/comprimidos_cev para su descarga
        os.rename(ruta_generado, ruta_comprimido)

        # Guardamos la ruta en el modelo con el identificador del proceso
        ModeloSeguimientoAulas.objects.filter(IdProceso=identificador_proceso).update(
            ArchivoComprimido=ruta_comprimido
        )

        respuesta = {
            "status": "success",
            "type": "info",
            "code": identificador_proceso,
        }

        # Volvemos al directorio de trabajo original
        os.chdir(settings.BASE_DIR)

        return respuesta

    # Caputramos el error y verificamos si es de tipo FileNotFoundError
    except FileNotFoundError:
        # Obtenemos el mensaje de error que se generó
        mensaje_error = str(sys.exc_info()[1])

        respuesta = {
            "status": "error",
            "type": "FileNotFoundError",
            "message": mensaje_error,
        }

        # Volvemos al directorio de trabajo original
        os.chdir(settings.BASE_DIR)

        return respuesta

    except ValueError:
        # Obtenemos el mensaje de error que se generó
        mensaje_error = str(sys.exc_info()[1])

        respuesta = {
            "status": "error",
            "type": "ValueError",
            "message": mensaje_error,
        }

        # Volvemos al directorio de trabajo original
        os.chdir(settings.BASE_DIR)

        return respuesta

    # Capturamos cualquier otro error
    except Exception:
        # Obtenemos el mensaje de error que se generó
        mensaje_error = str(sys.exc_info()[1])

        respuesta = {
            "status": "error",
            "type": "Exception",
            "message": mensaje_error,
        }

        # Volvemos al directorio de trabajo original
        os.chdir(settings.BASE_DIR)

        return respuesta


@verificar_miembro_grupo_seguridad(grupo_seguridad=GRUPOS_SEGURIDAD[nombre_grupo_seg])
@settings.AUTH.login_required(scopes="GroupMember.Read.All".split())
@require_http_methods(["POST"])
def GenerarReportesSeguimiento(request, *, context):

    identificador_usuario = obtener_usuario_id(context)

    form = FormularioSeguimientoAulas(request.POST, request.FILES)
    if form.is_valid():

        identificador_proceso = generar_codigo()

        # Agregamos el código del proceso al formulario
        form.instance.IdProceso = identificador_proceso
        form.instance.IdUsuario = identificador_usuario

        # Guardamos el formulario
        form.save()

        # Obtenemos el nombre del coordinador
        nombre_coordinador = form.cleaned_data["NombreCoordinador"]

        json_respuesta = elaborar_reportes(identificador_proceso, nombre_coordinador)

        return JsonResponse(json_respuesta, safe=False)


@verificar_miembro_grupo_seguridad(grupo_seguridad=GRUPOS_SEGURIDAD[nombre_grupo_seg])
@settings.AUTH.login_required(scopes="GroupMember.Read.All".split())
@require_http_methods(["GET"])
def SeguimientoAulas(request, *, context):
    
    info_usr = informacion_usuario(context)

    formulario = FormularioSeguimientoAulas()
    return render(
        request,
        "ReportesCEV/SeguimientoAulas.html",
        {
            "formulario": formulario,
            "nombre_usuario": info_usr["nombre_usuario"],
            "grupos_pertenece": info_usr["grupos_pertenece"],
            "grupos_seguridad": info_usr["grupos_seguridad"],
        },
    )


@verificar_miembro_grupo_seguridad(grupo_seguridad=GRUPOS_SEGURIDAD[nombre_grupo_seg])
@require_http_methods(["GET"])
@settings.AUTH.login_required(scopes="GroupMember.Read.All".split())
def DescargarReporteSeguimientoAulas(request, *, context, identificador_proceso):

    info_usr = informacion_usuario(context)

    identificador_usuario = obtener_usuario_id(context)

    # Verificamos si el usuario que solicita la descarga es el mismo que generó el proceso
    UsuarioProceso = ModeloSeguimientoAulas.objects.get(
        IdProceso=identificador_proceso
    ).IdUsuario

    if identificador_usuario != UsuarioProceso:
        messages.error(request, "No tienes permiso para descargar este archivo")
        return render(request, "ReportesCEV/SeguimientoAulas.html")

    # Obtenemos la ruta del archivo comprimido
    archivo_comprimido = ModeloSeguimientoAulas.objects.get(
        IdProceso=identificador_proceso
    ).ArchivoComprimido

    # Generamos la ruta al archivo comprimido
    ruta_archivo = os.path.join(MEDIA_ROOT, str(archivo_comprimido))

    try:
        # Leemos el archivo
        with open(ruta_archivo, "rb") as archivo:
            contenido = archivo.read()

        # Generamos la respuesta
        response = HttpResponse(contenido, content_type="application/zip")
        response["Content-Disposition"] = (
            f"attachment; filename=Seguimiento{identificador_proceso}.zip"
        )

        return response
    except FileNotFoundError:
        messages.error(request, "No se encontró el archivo comprimido")
        return render(
            request,
            "ReportesCEV/SeguimientoAulas.html",
            {
                "nombre_usuario": info_usr["nombre_usuario"],
                "grupos_pertenece": info_usr["grupos_pertenece"],
                "grupos_seguridad": info_usr["grupos_seguridad"],
            },
        )
