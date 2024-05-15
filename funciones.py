# Librerías necesarias
import pandas as pd
import os
import argparse

# Constantes

# Directorio donde se guardan los archivos temporales
DIRECTORIO = "/srv/www/servicios/tmp/"

# Funciones


def generar_codigo():
    """
    Genera un código único con la fecha y hora actual.

    Returns:
        str: Código único con la fecha y hora actual.
    """
    return pd.Timestamp.now().strftime("%Y%m%d%H%M%S")


def reemplazar_datos(texto, df_revision, n):
    """
    Reemplaza los marcadores de posición en un texto con los valores correspondientes
    de un DataFrame en una fila específica.

    Args:
    texto (str): El texto que contiene los marcadores de posición a reemplazar.
    df_revision (DataFrame): El DataFrame que contiene los datos para el reemplazo.
    n (int): El índice de la fila en el DataFrame de donde se tomarán los datos.

    Returns:
    str: El texto con los marcadores de posición reemplazados por los valores correspondientes.
    """
    # Diccionario de sustituciones
    reemplazos = {
        "<<Docente>>": df_revision["Nombre Completo"][n],
        "<<NRC>>": str(int(df_revision["NRC"][n])),
        "<<Dominio>>": df_revision["Dominio"][n],
        "<<Facultad>>": str(df_revision["Facultad"][n]),
        "<<Carrera>>": str(df_revision["Carrera"][n]),
        "<<Recursos>>": df_revision["Recursos"][n],
        "<<Evaluación>>": df_revision["Evaluación"][n],
        "<<Estructura>>": df_revision["Estructura"][n],
        "<<Calificaciones>>": df_revision["Calificaciones"][n],
        "<<Retroalimentación>>": df_revision["Retroalimentación"][n],
        "<<Fecha>>": (
            df_revision["Fecha"][n].strftime("%m/%d/%Y")
            if hasattr(df_revision["Fecha"][n], "strftime")
            else str(df_revision["Fecha"][n])
        ),
        "<<Hora>>": str(df_revision["Hora"][n]),
    }

    # Reemplazo de texto usando el diccionario
    for marcador, valor in reemplazos.items():
        texto = texto.replace(marcador, valor)

    return texto


def leer_archivo_revision(archivo_revision):
    """
    Lee el archivo de revisión y genera un DataFrame con los datos necesarios.

    Args:
    archivo_revision (str): La ruta al archivo de revisión en formato Excel.

    Returns:
    DataFrame: Un DataFrame con los datos de la revisión.
    """
    # Leemos el archivo de revisión
    df_revision = pd.read_excel(archivo_revision, sheet_name="Observación de aulas")

    # Renombramos las columnas
    df_revision.columns = [
        "Dominio",
        "Facultad",
        "Carrera",
        "NRC",
        "Apellidos",
        "Nombre",
        "Fecha",
        "Hora",
        "Recursos",
        "Evaluación",
        "Estructura",
        "Calificaciones",
        "Retroalimentación",
    ]

    # Eliminamos todos los registros que tengan NaN en la columna Nombre
    df_revision = df_revision.dropna(subset=["Nombre"])

    # Concatenamos los nombres y apellidos
    df_revision["Nombre Completo"] = (
        df_revision["Apellidos"] + " " + df_revision["Nombre"]
    )

    return df_revision


def procesar_seguimiento(archivo_revision, nombre_coordinador):
    """
    Procesa el seguimiento de aulas basado en un archivo de revisión y genera archivos .tex
    y un archivo .zip con los resultados.

    Parámetros:
    archivo_revision (str): La ruta al archivo de revisión en formato Excel.
    nombre_coordinador (str): El nombre del coordinador a incluir en los archivos generados.

    Retorna:
    bytes: El contenido del archivo .zip generado.
    """
    # Creamos un código temporal para generar los archivos con la fecha y hora
    seguimiento = generar_codigo()

    # Generamos el DataFrame con los datos de revisión
    df_revision = leer_archivo_revision(archivo_revision)

    # Generamos una lista con los nombres de los docentes sin repetir
    lista_docentes = df_revision["Nombre Completo"].unique()

    # Creamos una carpeta por cada docente, dentro de la carpeta Seguimiento
    for docente in lista_docentes:
        # Directorio para la creación de la carpeta
        dir_carpeta = os.path.join(DIRECTORIO, f"Seguimiento{seguimiento}/{docente}")
        if not os.path.exists(dir_carpeta):
            os.makedirs(dir_carpeta)

    # Leemos la plantilla
    texto_base = open("formato.tex", "r", encoding="utf-8").read()

    # Reemplazo del nombre del coordinador
    texto_base = texto_base.replace("<<Coordinador>>", nombre_coordinador)

    # Recorremos cada fila de los datos
    for n in range(df_revision.shape[0]):
        # Generamos un archivo con el nombre del docente y NRC
        nombre_archivo = f"{int(df_revision['NRC'][n])}-Seguimiento{seguimiento}.tex"
        ruta_archivo = os.path.join(
            DIRECTORIO,
            f"Seguimiento{seguimiento}/{df_revision['Nombre Completo'][n]}/{nombre_archivo}",
        )

        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            # Reemplazamos los datos en el texto base
            texto = reemplazar_datos(texto_base, df_revision, n)
            # Escribimos el texto en el nuevo archivo
            archivo.write(texto)

        # Directorios para compilación y archivo
        dir_carpeta_compilacion = os.path.join(
            DIRECTORIO, f"Seguimiento{seguimiento}/{df_revision['Nombre Completo'][n]}"
        )
        dir_archivo = os.path.join(
            dir_carpeta_compilacion,
            f"{int(df_revision['NRC'][n])}-Seguimiento{seguimiento}",
        )

        # Compilamos el archivo tex (2 veces)
        os.system(
            f'pdflatex -output-directory="{dir_carpeta_compilacion}" "{dir_archivo}.tex"'
        )
        os.system(
            f'pdflatex -output-directory="{dir_carpeta_compilacion}" "{dir_archivo}.tex"'
        )
        
        # Eliminamos los archivos auxiliares
        for ext in [".aux", ".log", ".tex"]:
            os.remove(f"{dir_archivo}{ext}")

    # Creamos un archivo zip con todo lo generado
    zip_path = os.path.join(DIRECTORIO, f"Seguimiento{seguimiento}.zip")
    os.system(
        f"zip -r {zip_path} {os.path.join(DIRECTORIO, f'Seguimiento{seguimiento}')}"
    )

    # Eliminamos la carpeta original
    os.system(f"rm -rf {os.path.join(DIRECTORIO, f'Seguimiento{seguimiento}')}")

    # Leemos el archivo zip
    with open(zip_path, "rb") as f:
        zip_file = f.read()

    # Regresamos el archivo zip
    return zip_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesar seguimiento de aulas.")
    parser.add_argument(
        "archivo_revision",
        type=str,
        help="Ruta al archivo de revisión en formato Excel",
    )
    parser.add_argument("nombre_coordinador", type=str, help="Nombre del coordinador")

    args = parser.parse_args()

    zip_file = procesar_seguimiento(args.archivo_revision, args.nombre_coordinador)

    # Guardar el archivo zip en la ubicación deseada
    zip_output_path = os.path.join(DIRECTORIO, "Seguimiento.zip")
    with open(zip_output_path, "wb") as f:
        f.write(zip_file)
