from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import FormularioSeguimientoAulas
import pandas as pd
from .reportes_cev import procesar_seguimiento
from .models import ModeloSeguimientoAulas
from ServiciosReportesPUCE.settings import (
    MEDIA_ROOT,
    DIRECTORIO_TEMPORAL_REPORTES_CEV,
    GRUPO_SEGURIDAD_REPORTES_CEV,
)
import os
from django.contrib import messages
from django.conf import settings
import sys
from ServiciosReportesPUCE.views import obtener_grupos
from functools import wraps
from ServiciosReportesPUCE.funciones import obtener_usuario_id,obtener_imagen_perfil 
import json


def verificar_miembro_grupo_seguridad(view_func):
    """
    Decorador para verificar si el usuario es miembro del grupo ServiciosPUCE.

    Este decorador extrae el token de sesión del usuario,
    luego extrae el secreto necesario del token y utiliza este secreto para obtener
    los grupos a los que pertenece el usuario. Si el usuario es miembro del grupo
    'GRUPO_SEGURIDAD_REPORTES_CEV', se permite el acceso a la vista.
    Si no, se redirige al usuario a la página de inicio del tablero.

    Args:
        view_func: La función de vista a decorar.

    Returns:
        Una función de envoltura que realiza la verificación de membresía.
    """

    @wraps(view_func)
    def envoltura(request, *args, **kwargs):
        # Manejar el caso donde no se encuentra el token en la sesión del usuario
        # Esto podría suceder si el usuario no está autenticado
        try:
            session_token_cache = json.loads(request.session["_token_cache"])
            acces_token = session_token_cache["AccessToken"]
            secret = list(acces_token.values())[0]["secret"]
        except json.JSONDecodeError:
            secret = None

        if secret:
            grupos = obtener_grupos(secret)
            if GRUPO_SEGURIDAD_REPORTES_CEV in grupos:
                return view_func(request, *args, **kwargs)

        # Redirigir al usuario a la página de inicio del tablero
        return redirect("InicioTablero")

    return envoltura



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


@verificar_miembro_grupo_seguridad
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


# @verificar_miembro_grupo_seguridad
@settings.AUTH.login_required(scopes="GroupMember.Read.All".split())
@require_http_methods(["GET"])
def SeguimientoAulas(request, *, context):
    usuario = context["user"]
    grupos_pertenece = obtener_grupos(context["access_token"])
    obtener_imagen_perfil(context["access_token"])

    formulario = FormularioSeguimientoAulas()
    return render(
        request,
        "ReportesCEV/SeguimientoAulas.html",
        {
            "formulario": formulario,
            "nombre_usuario": usuario["name"],
            "grupos_pertenece": grupos_pertenece,
        },
    )


@verificar_miembro_grupo_seguridad
@require_http_methods(["GET"])
@settings.AUTH.login_required(scopes="GroupMember.Read.All".split())
def DescargarReporteSeguimientoAulas(request, *, context, identificador_proceso):
    usuario = context["user"]
    grupos_pertenece = obtener_grupos(context["access_token"])
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
                "nombre_usuario": usuario["name"],
                "grupos_pertenece": grupos_pertenece,
            },
        )
