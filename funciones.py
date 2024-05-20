# Librerías necesarias
import pandas as pd
import os
import shutil
import argparse
import zipfile

# Constantes

# Directorio donde se guardan los archivos temporales
DIRECTORIO = "."
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

    # Reviso que tenga el número correcto de columnas
    if not os.path.exists(archivo_revision):
        raise FileNotFoundError(
            f"No se encontró el archivo de revisión '{archivo_revision}'."
        )
    if df_revision.shape[1] != 13:
        raise ValueError(
            f"El archivo de revisión debe tener 13 columnas, pero tiene {df_revision.shape[1]}."
        )

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


def procesar_seguimiento(
    archivo_revision,
    nombre_coordinador,
    directorio=DIRECTORIO,
    seguimiento=generar_codigo(),
):
    """
    Procesa el seguimiento de aulas basado en un archivo de revisión y genera archivos .tex
    y un archivo .zip con los resultados.

    Args:
    archivo_revision (str): La ruta al archivo de revisión en formato Excel.
    nombre_coordinador (str): El nombre del coordinador a incluir en los archivos generados.
    directorio (str): Directorio donde se generará el seguimiento.

    Returns:
    bytes: El contenido del archivo .zip generado.
    """
    # Revisamos que existan los archivos necesarios
    if not os.path.exists("formato.tex"):
        raise FileNotFoundError("No se encontró el archivo 'formato.tex'.")
    if not os.path.exists("HojaMembretadaCEV.pdf"):
        raise FileNotFoundError("No se encontró el archivo 'HojaMembretadaCEV.pdf'.")
    if not os.path.exists(archivo_revision):
        raise FileNotFoundError(
            f"No se encontró el archivo de revisión '{archivo_revision}'."
        )

    # Generamos el DataFrame con los datos de revisión
    df_revision = leer_archivo_revision(archivo_revision)

    # Generamos una lista con los nombres de los docentes sin repetir
    lista_docentes = df_revision["Nombre Completo"].unique()

    # Creamos una carpeta por cada docente, dentro de la carpeta Seguimiento
    for docente in lista_docentes:
        # Directorio para la creación de la carpeta
        dir_carpeta = os.path.join(directorio, f"Seguimiento-{seguimiento}/{docente}")
        if not os.path.exists(dir_carpeta):
            os.makedirs(dir_carpeta)

    # Leemos la plantilla
    texto_base = open("formato.tex", "r", encoding="utf-8").read()

    # Reemplazo del nombre del coordinador
    texto_base = texto_base.replace("<<Coordinador>>", nombre_coordinador)

    # Recorremos cada fila de los datos
    for n in range(df_revision.shape[0]):
        # Generamos un archivo con el nombre del docente y NRC
        nombre_archivo = f"{int(df_revision['NRC'][n])}-Seguimiento.tex"
        ruta_archivo = os.path.join(
            directorio,
            f"Seguimiento-{seguimiento}/{df_revision['Nombre Completo'][n]}/{nombre_archivo}",
        )

        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            # Reemplazamos los datos en el texto base
            texto = reemplazar_datos(texto_base, df_revision, n)
            # Escribimos el texto en el nuevo archivo
            archivo.write(texto)

        # Directorios para compilación y archivo
        dir_carpeta_compilacion = os.path.join(
            directorio, f"Seguimiento-{seguimiento}/{df_revision['Nombre Completo'][n]}"
        )
        dir_archivo = os.path.join(
            dir_carpeta_compilacion,
            f"{int(df_revision['NRC'][n])}-Seguimiento",
        )

        # Compilamos el archivo tex (2 veces)
        try:
            os.system(
                f'pdflatex -output-directory="{dir_carpeta_compilacion}" "{dir_archivo}.tex"'
            )
            os.system(
                f'pdflatex -output-directory="{dir_carpeta_compilacion}" "{dir_archivo}.tex"'
            )
        except Exception as e:
            print(f"Error al compilar el archivo {dir_archivo}.")
            print(e)

        # Eliminamos los archivos auxiliares
        for ext in [".aux", ".log", ".tex"]:
            os.remove(f"{dir_archivo}{ext}")

    # Creamos la ruta del archivo zip
    zip_path = os.path.join(directorio, f"Seguimiento-{seguimiento}.zip")

    # Creamos la ruta de la carpeta a comprimir
    carpeta_a_comprimir = os.path.join(directorio, f"Seguimiento-{seguimiento}")

    # Creamos un archivo zip
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(carpeta_a_comprimir):
            for file in files:
                file_path = os.path.join(root, file)
                # Agregar el archivo al zip con la ruta relativa a la carpeta
                zipf.write(file_path, os.path.relpath(file_path, carpeta_a_comprimir))

    # Eliminar la carpeta original y su contenido
    shutil.rmtree(carpeta_a_comprimir)

    # Regresamos el archivo zip
    return zip_path


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
