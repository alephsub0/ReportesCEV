from django import forms

# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True

# class MultipleFileField(forms.FileField):
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault("widget", MultipleFileInput())
#         super().__init__(*args, **kwargs)

#     def clean(self, data, initial=None):
#         single_file_clean = super().clean
#         if isinstance(data, (list, tuple)):
#             result = [single_file_clean(d, initial) for d in data]
#         else:
#             result = [single_file_clean(data, initial)]
#         return result


# class FileFieldForm(forms.Form):
#     file_field = MultipleFileField()

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