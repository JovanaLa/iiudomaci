from flask import Flask, request
import os
import psycopg2
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

BROJ_DANA = (
    """SELECT COUNT(DISTINCT DATE(datum)) AS dani FROM vlaznostvazduha;"""
)

GLOBAL_PROSEK = """SELECT AVG(vlaznostvazduhasobe) as prosek FROM vlaznostvazduha;"""

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.post("/api/room")
def create_soba():
    data = request.get_json()
    ime = data["ime"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_SOBE_TABLE)
            cursor.execute(INSERT_SOBA_RETURN_ID, (ime,))
            soba_id = cursor.fetchone()[0]

    return {"id": soba_id, "poruka": f"Soba {ime} je kreirana."}, 201