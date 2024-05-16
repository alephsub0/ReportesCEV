from django import forms
from ReportesCEV.models import ModeloSeguimientoAulas

class FormularioSeguimientoAulas(forms.ModelForm):
    class Meta:
        model = ModeloSeguimientoAulas
        fields = ['NombreCoordinador','ArchivoSeguimiento','IdProceso']