from flask import Flask, request
import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv


CREATE_SOBE_TABLE = (
    "CREATE TABLE IF NOT EXISTS sobe (id SERIAL PRIMARY KEY, ime TEXT);"
)

CREATE_VLAZNOSTVAZDUHA_TABLE = """CREATE TABLE IF NOT EXISTS vlaznostvazduha (soba_id INTEGER, vlaznostvazduhasobe REAL,
                         datum TIMESTAMP, FOREIGN KEY(soba_id) REFERENCES sobe(id) ON DELETE CASCADE);"""

INSERT_SOBA_RETURN_ID = "INSERT INTO sobe (ime) VALUES (%s) RETURNING id;"

INSERT_VV = (
    "INSERT INTO vlaznostvazduha (soba_id, vlaznostvazduhasobe, datum) VALUES (%s, %s, %s);"
)
DELETE_SOBA_BY_ID = ("DELETE FROM sobe WHERE id = '%s';")



BROJ_DANA = (
    """SELECT COUNT(DISTINCT DATE(datum)) AS dani FROM vlaznostvazduha;"""
)

 
GLOBAL_PROSEK = """SELECT AVG(vlaznostvazduhasobe) as prosek FROM vlaznostvazduha;"""

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.post("/api/soba")
def create_soba():
    data = request.get_json()
    ime = data["ime"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_SOBE_TABLE)
            cursor.execute(INSERT_SOBA_RETURN_ID, (ime,))
            soba_id = cursor.fetchone()[0]

    return {"id": soba_id, "poruka": f"Soba {ime} je kreirana."}, 201



@app.post("/api/vlaznostvazduha")
def add_vlaznostvazduha():
    data = request.get_json()
    vlaznostvazduhasobe = data["vlaznostvazduhasobe"]
    soba_id = data["soba_id"]
    try:
         datum = datetime.strptime(data["datum"], "%d/%m/%Y  %H:%M:%S")
    except KeyError:
        datum = datetime.now(timezone.utc)

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_VLAZNOSTVAZDUHA_TABLE)
            cursor.execute(INSERT_VV, (soba_id, vlaznostvazduhasobe, datum))

    return {"poruka": "Dodata vlaznost vazduha."}, 201


@app.get("/api/prosek")
def get_prosek():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GLOBAL_PROSEK)
            prosek = cursor.fetchone()[0]
            cursor.execute(BROJ_DANA)
            dani = cursor.fetchone()[0]

    return {"prosek": round(prosek, 2), "dani": dani}


@app.delete("/api/sobe")
def delete_soba():
    data = request.get_json()
    soba_id = data["id"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_SOBA_BY_ID, (soba_id,))
            deleted_count = cursor.rowcount
        if deleted_count == 0:
                return {"poruka": f"Soba sa id-jem {soba_id} ne postoji."}, 404

    return {"poruka": f"Soba sa id-jem {soba_id} uspešno obrisana."}, 200

if __name__ == "__main__":
    app.run(debug=True ,port=8080,use_reloader=False)