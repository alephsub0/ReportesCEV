import os
import pandas as pd
import zipfile as zf
import openai

# Función para el chat
def ChatGPT(entrada, contexto="", modelo="GPT-3.5"):
    respuesta = openai.chat.completions.create(    
        model=modelo,
        messages=[{"role": "system", "content": contexto},
                  {"role": "user", "content": entrada}]
    )
    return respuesta.choices[0].message.content

def calificar(file_ex, file_gr, instruccion, api_key, modelo):
    # Leo el archivo csv
    df = pd.read_csv(file_gr)
    # Abro el archivo zip
    carpeta = file_ex.split('.')[0]
    # Descomprimo el archivo zip
    with zf.ZipFile(file_ex, 'r') as zip_ref:
        zip_ref.extractall(carpeta)
    zip_ref.close()

    # Api key
    openai.api_key = api_key
    
    # Contexto para el modelo
    contexto = """Vas a calificar un examen, te daré la petición y la respuesta dada por el estudiante. Indicarás la retroalimentación breve e indicarás la calificación en formato de tabla en el siguiente formato (no agregues formato adicional):
        Retroalimentación: 
        Calificación: 1.0"""

    # Instrucción
    instruccion = "Calcule la inversa por el método de Gauss Jordan, explicando cada paso. (2 puntos) "

    # Cambio la calificación y la retroalimentación a NaN
    df['Calificación'] = None
    df['Comentarios de retroalimentación'] = None

    # Recorro los archivos
    for archivo in os.listdir(carpeta):
        # Nombre del estudiante
        estudiante = archivo.split('_')[0]
        # Leo el archivo json
        with open(carpeta + '/' + archivo, 'r') as file:
            data = file.read()
            # Realizo la petición
            respuesta = ChatGPT(instruccion + " Respuesta: " + data, contexto=contexto, modelo = modelo)
            print(respuesta)
            # Extraigo la calificación
            calificacion = respuesta.split('Calificación: ')[1]
            calificacion = calificacion.replace('\n', '').strip()
            # Extraigo la retroalimentación
            retroalimentacion = respuesta.split('Retroalimentación: ')[1].split('Calificación: ')[0]
            retroalimentacion = retroalimentacion.replace('\n', '').strip()
            # Agrego la calificación y la retroalimentación al dataframe
            df.loc[df['Nombre completo'] == estudiante, 'Calificación'] = calificacion
            df.loc[df['Nombre completo'] == estudiante, 'Comentarios de retroalimentación'] = retroalimentacion
            # Pausa de 30 segundos
            # time.sleep(30)     

    # Guardo el dataframe
    df.to_csv(file_ex.split('.')[0] + '_calificado.csv', index=False, encoding='utf-8-sig')

    return df

