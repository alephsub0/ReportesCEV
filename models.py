from django.db import models


class ModeloSeguimientoAulas(models.Model):
    IdArchivoSeguimiento = models.AutoField(
        primary_key=True, db_column="IdArchivoSeguimiento"
    )
    NombreCoordinador = models.CharField(max_length=100, db_column="NombreCoordinador")
    ArchivoSeguimiento = models.FileField(
        upload_to="reportes_cev/", db_column="ArchivoSeguimiento"
    )
    Correo = models.CharField(max_length=150, db_column="Correo")
    CorreoEnviado = models.SmallIntegerField(blank=True, null=True, db_column="CorreoEnviado")
    IdProceso = models.IntegerField(blank=True, null=False, db_column="IdProceso")
    IdUsuario = models.IntegerField(blank=True, null=False, db_column="IdUsuario")
    Fecha = models.DateTimeField(auto_now_add=True, db_column="Fecha")
    ArchivoComprimido = models.CharField(
        max_length=100, blank=True, null=True, db_column="ArchivoComprimido"
    )


    class Meta:
        managed = True
        db_table = "SeguimientoAulas"
