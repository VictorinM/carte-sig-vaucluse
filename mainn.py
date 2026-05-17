ffrom fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="leaflet",
        user="postgres",
        password="02@Maxivito@02"
    )

@app.get("/")
def accueil():
    return {"message": "Bonjour, je suis ton API SIG !"}

@app.get("/sites-velo")
def get_sites_velo():
    import json
    with open("site de visite accessible en vélo.geojson", encoding="utf-8") as f:
        donnees = json.load(f)
    return donnees

@app.get("/sites-velo/{commune}")
def get_sites_par_commune(commune: str):
    import json
    with open("site de visite accessible en vélo.geojson", encoding="utf-8") as f:
        donnees = json.load(f)
    sites_filtres = [
        feature for feature in donnees["features"]
        if feature["properties"]["Commune"] == commune
    ]
    return {
        "type": "FeatureCollection",
        "features": sites_filtres
    }

@app.get("/hebergements-velo")
def get_hebergements_velo():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        'nom', "Nom",
                        'commune', "Commune"
                    )
                )
            )
        )
        FROM (SELECT * FROM "hebergement accessible en vélo" LIMIT 10) as t
    """)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result
@app.get("/hebergements-proche/{longitude}/{latitude}/{rayon}")
def get_hebergements_proche(longitude: float, latitude: float, rayon: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        'nom', "Nom",
                        'commune', "Commune"
                    )
                )
            )
        )
        FROM "hebergement accessible en vélo"
        WHERE ST_DWithin(
            geom::geography,
            ST_MakePoint(%s, %s)::geography,
            %s
        )
    """, (longitude, latitude, rayon))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result