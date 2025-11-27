from flask import Flask, render_template, request
from services.mongo_client import *
from services.graph_visualizer import generar_grafo
from services.mongo_client import obtener_similitudes_umbral, obtener_detalles_nodos

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

# 1. Buscar por nombre
@app.route("/buscar-nombre", methods=["GET", "POST"])
def buscar_nombre_page():
    resultado = None
    buscado = False
    if request.method == "POST":
        buscado = True
        nombre = request.form["nombre"]
        resultado = buscar_por_nombre(nombre)
    return render_template("buscar_nombre.html", resultado=resultado, buscado=buscado)

# 2. Detalle paginado de una providencia
@app.route("/detalle/<nombre>/<int:pagina>")
def detalle_providencia(nombre, pagina):

    data = buscar_por_nombre(nombre)
    if not data:
        return "Providencia no encontrada", 404

    texto = data["texto"]
    tam_pagina = 3000

    inicio = pagina * tam_pagina
    fin = inicio + tam_pagina

    fragmento = texto[inicio:fin]

    hay_anterior = pagina > 0
    hay_siguiente = fin < len(texto)

    return render_template(
        "detalle.html",
        data=data,
        fragmento=fragmento,
        pagina=pagina,
        hay_anterior=hay_anterior,
        hay_siguiente=hay_siguiente
    )

# 3. Buscar por tipo
@app.route("/buscar-tipo", methods=["GET", "POST"])
def buscar_tipo_page():
    resultados = None
    buscado = False
    if request.method == "POST":
        buscado = True
        tipo = request.form["tipo"]
        resultados = buscar_por_tipo(tipo)
    return render_template("buscar_tipo.html", resultados=resultados, buscado=buscado)

# 4. Buscar por texto
@app.route("/buscar-texto", methods=["GET", "POST"])
def buscar_texto_page():
    resultados = None
    buscado = False
    if request.method == "POST":
        buscado = True
        texto = request.form["texto"]
        resultados = buscar_por_texto(texto)
    return render_template("buscar_texto.html", resultados=resultados, buscado=buscado)

# 5. Buscar similitudes
@app.route("/similitudes", methods=["GET", "POST"])
def similitudes_page():
    resultados = None
    buscado = False
    if request.method == "POST":
        buscado = True
        nombre = request.form["nombre"]
        resultados = buscar_similitudes(nombre)
    return render_template("similitudes.html", resultados=resultados, buscado=buscado)

# 6. Grafo filtrado por umbral
@app.route("/grafo", methods=["GET", "POST"])
def grafo_page():
    umbral = 0.5
    if request.method == "POST":
        umbral = float(request.form["umbral"])

    similitudes = obtener_similitudes_umbral(umbral) 
    detalles = obtener_detalles_nodos(similitudes)

    # Calcular número total de nodos únicos
    nodos = set()
    for s in similitudes:
        nodos.add(s["providencia_1"])
        nodos.add(s["providencia_2"])

    n = len(nodos)
    total_relaciones = n * (n - 1) // 2   # fórmula combinaciones

    ruta = generar_grafo(similitudes, detalles)

    return render_template(
        "grafo.html",
        grafo="/" + ruta,
        umbral=umbral,
        total_relaciones=total_relaciones
    )

if __name__ == "__main__":
    app.run(debug=True)
