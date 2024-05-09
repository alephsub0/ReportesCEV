from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from .forms import FormularioSeguimientoAulas,FormularioArchivosCalificador
import pandas as pd
from .funciones import ProcesarSeguimiento


# Create your views here.
@login_required
def Inicio(request):
    return render(request, 'InicioTablero.html')

@login_required
def SeguimientoAulas(request):
    if request.method == "GET":

        formulario = FormularioSeguimientoAulas()
        return render(request, 'SeguimientoAulas.html',{'formulario':formulario})
    
    elif request.method == "POST":

        form = FormularioSeguimientoAulas(request.POST, request.FILES)
        if form.is_valid():
            ArchivoEXCEL = form.cleaned_data["ArchivoSeguimiento"]

            archivo = ProcesarSeguimiento(ArchivoEXCEL)

            response = HttpResponse(archivo, content_type='application/zip')
            # Define el nombre del archivo ZIP que se descargará
            zip_filename = 'archivo_comprimido.zip'
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
            return response

        return render(request, 'SeguimientoAulas.html')

# def Calificador(request):
#     if request.method == "GET":
#         return render(request, 'SeguimientoAulas.html')
#     else:


#         API_key = request.POST['api_key']
#         Modelo = request.POST['modelo']
#         Instruccion = request.POST['instruccion']
#         ArchivoZIP = request.FILES['file_ex']
#         ArchivoCSV = request.FILES['file_gr']

#         df = pd.read_csv(ArchivoCSV)
#         print(df.head())

#         print(request.FILES)
#         print(ArchivoCSV)


#         return render(request, 'SeguimientoAulas.html')

