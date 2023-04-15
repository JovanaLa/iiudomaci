from flask import Flask
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

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.get("/")
def home():
    return "Hello world"