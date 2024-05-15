from django import forms

# Create your models here.
class FormularioArchivosCalificador(forms.Form):
    APIKey = forms.CharField(max_length=100)
    ModeloGPT = forms.CharField(max_length=50)
    ArchivosExamenes = forms.FileField()
    ArchivoCalificaciones = forms.FileField()

class FormularioSeguimientoAulas(forms.Form):
    ArchivoSeguimiento = forms.FileField()
    # ArchivoHojaMembretada = forms.FileField()
    NombreCoordinador = forms.CharField(max_length=100, required=True)