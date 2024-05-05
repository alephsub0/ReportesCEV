from flask import Flask, render_template, request
from codigo import calificador

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    instruccion = None
    api_key = None
    modelo = None
    file_ex = None
    file_gr = None
    calificaciones = None
    tabla_html = None
    if request.method == 'POST':
        api_key = request.form['api_key']
        modelo = request.form['modelo']
        file_ex = request.form['file_ex']
        file_gr = request.form['file_gr']
        instruccion = request.form['instruccion']
        calificaciones = calificador.calificar(file_ex, file_gr, instruccion, api_key, modelo)
        tabla = calificaciones[['Nombre completo', 'Calificación', 'Comentarios de retroalimentación']]
        tabla_html = tabla.to_html(index=False)
        print(tabla_html)
    return render_template('index.html', instruccion=instruccion, api_key=api_key, modelo=modelo, file_ex=file_ex, file_gr=file_gr, calificaciones=calificaciones, tabla=tabla_html)


@app.route('/rubrica')
def rubrica():
    return render_template('rubrica.html')


@app.route('/help')
def help():
    return render_template('help.html')


if __name__ == '__main__':
    app.run(debug=True)