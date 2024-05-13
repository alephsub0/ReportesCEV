# importo pandas
import pandas as pd
# importo os
import os

Directorio = '/srv/www/servicios/tmp/'

def GenerarCodigo():
    return pd.Timestamp.now().strftime("%Y%m%d%H%M%S")

def ProcesarSeguimiento(archivo_revision,NombreCoordinador):

    # Creamos un idtemporal para generar los archivos con la fecha y hora
    seguimiento = GenerarCodigo()

    df_revision = pd.read_excel(archivo_revision,sheet_name="Observación de aulas")
    # renombro las columnas
    df_revision.columns = ['Dominio','Facultad','Carrera','NRC','Apellidos','Nombre','Fecha','Hora','Recursos','Evaluación', 'Estructura', 'Calificaciones', 'Retroalimentación']
    # Elimino todos los registro que en Nombre tengan NaN
    df_revision = df_revision.dropna(subset=['Nombre'])

    # concateno los nombres y apellidos
    df_revision['Nombre Completo'] = df_revision['Apellidos'] + " " + df_revision['Nombre']
    # genero una lista con los nombres de los docentes sin repetir
    lista_docentes = df_revision['Nombre Completo'].unique()
    # creo una carpeta por cada docente, dentro de la carpeta Seguimiento

    for docente in lista_docentes:
        # directorio para la creación de la carpeta
        dir_carpeta = os.path.join(Directorio,f"Seguimiento{seguimiento}/"+docente)

        if not os.path.exists(dir_carpeta):
            os.makedirs(dir_carpeta)

    # genero una función que me permita reemplazar los datos de la tabla de evaluación
    def reemplazar(texto, n):
        # reemplazo la información de la tabla de revision
        # Nombre docente
        texto = texto.replace("<<Docente>>", df_revision['Nombre Completo'][n])
        # NRC
        texto = texto.replace("<<NRC>>", str(int(df_revision['NRC'][n])))
        # Dominio
        texto = texto.replace("<<Dominio>>", df_revision['Dominio'][n])
        # Facultad
        texto = texto.replace("<<Facultad>>", str(df_revision['Facultad'][n]))
        # Carrera
        texto = texto.replace("<<Carrera>>", str(df_revision['Carrera'][n]))
        # Recursos
        texto = texto.replace("<<Recursos>>", df_revision['Recursos'][n])
        # Evaluación
        texto = texto.replace("<<Evaluación>>", df_revision['Evaluación'][n])
        # Estructura
        texto = texto.replace("<<Estructura>>", df_revision['Estructura'][n])
        # Calificaciones
        texto = texto.replace("<<Calificaciones>>", df_revision['Calificaciones'][n])
        # Retroalimentación
        texto = texto.replace("<<Retroalimentación>>", df_revision['Retroalimentación'][n])
        # Fecha
        try:
            texto = texto.replace("<<Fecha>>", df_revision['Fecha'][n].strftime("%m/%d/%Y"))
        except:
            texto = texto.replace("<<Fecha>>", str(df_revision['Fecha'][n]))
        # Hora
        texto = texto.replace("<<Hora>>", str(df_revision['Hora'][n]))
        # Coordinador
        texto = texto.replace("<<Coordinador>>", NombreCoordinador)
        return texto

    # Recorro cada fila de los datos
    for n in range(df_revision.shape[0]):
    # for n in range(1):
        # Genero un archivo con el nombre
        archivo = open(Directorio+f"Seguimiento{seguimiento}/{df_revision['Nombre Completo'][n]}/{int(df_revision['NRC'][n])}-Seguimiento{seguimiento}.tex" , "w", encoding="utf-8")
        # Abro el archivo de formato
        formato = open("formato.tex" , "r", encoding="utf-8")
        # Tomo el texto del formato
        texto = formato.read()
        # Reemplazo los datos de la tabla de evaluación
        texto = reemplazar(texto, n)
        # Escribo en el nuevo archivo el texto del formato reemplazando los datos
        archivo.write(texto)
        # Cierro los archivos
        archivo.close()
        formato.close()
        # compilo el archivo tex
        # dir_carpeta = Directorio+f"Seguimiento{seguimiento}/{df_revision['Nombre Completo'][n]}"
        # utilizamos join para unir Directorio con el texto anterior
        dir_carpeta_compilacion = os.path.join(Directorio,f"Seguimiento{seguimiento}/{df_revision['Nombre Completo'][n]}")
        dir_archivo = Directorio+f"Seguimiento{seguimiento}/{df_revision['Nombre Completo'][n]}/{int(df_revision['NRC'][n])}-Seguimiento{seguimiento}"
        os.system(f'pdflatex -output-directory="{dir_carpeta_compilacion}" "{dir_archivo}.tex"')
        # elimino los archivos auxiliares
        os.remove(f"{dir_archivo}.aux")
        os.remove(f"{dir_archivo}.log")
        os.remove(f"{dir_archivo}.tex")
    
    # Creamos un archivo zip con todo lo generado
    os.system(f'zip -r {Directorio}Seguimiento{seguimiento}.zip {Directorio}Seguimiento{seguimiento}')

    # Eliminamos la carpeta original
    os.system(f'rm -rf {Directorio}Seguimiento{seguimiento}')

    # Leemos el archivo zip
    with open(Directorio+f'Seguimiento{seguimiento}.zip', 'rb') as f:
        zip_file = f.read()
    
    # Regresamos el archivo zip 
    return zip_file





