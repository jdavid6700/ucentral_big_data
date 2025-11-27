from pymongo import MongoClient
import yaml

config = yaml.safe_load(open("config/config.yaml"))

client = MongoClient(config["mongo"]["uri"])
db = client[config["mongo"]["db"]]

# Colecciones
prov = db[config["mongo"]["coll1"]]
sims = db[config["mongo"]["coll2"]]

def buscar_por_nombre(nombre):
    return prov.find_one({"providencia": nombre})

def buscar_por_tipo(tipo):
    return list(prov.find({"tipo": tipo}))

def buscar_por_texto(texto):
    prov.create_index([("texto", "text")])
    return list(prov.find({"$text": {"$search": texto}}))

def buscar_similitudes(nombre):
    return list(sims.find({
        "$or": [
            {"providencia_1": nombre},
            {"providencia_2": nombre}
        ]
    }))

def obtener_similitudes_umbral(umbral):
    return list(sims.find({"similaridad": {"$gte": umbral}}))

def obtener_detalles_nodos(similitudes):
    """
    Construye un diccionario con la información básica de cada providencia
    presente en la lista de similitudes.
    """

    nodos = set()

    # Extraer todos los nombres de providencia de la lista
    for s in similitudes:
        # según tu base, los campos se llaman PROVIDENCIA_1 y PROVIDENCIA_2
        nodos.add(s["providencia_1"])
        nodos.add(s["providencia_2"])

    detalles = {}

    # Consultar cada uno en Mongo
    for nombre in nodos:
        doc = prov.find_one({"providencia": nombre})
        if doc:
            detalles[nombre] = {
                "tipo": doc.get("tipo", "Desconocido"),
                "anio": doc.get("anio", "N/A"),
                "texto": doc.get("texto", "")
            }

    return detalles

