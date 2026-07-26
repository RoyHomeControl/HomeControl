# %%
import requests, json
from datetime import datetime, timezone
from secret import *
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

COUCH_URL = "http://100.108.137.1:5984"
COUCH_DB = "homecontrol"


def couch_get(doc_id: str):
    response = requests.get(
        f"{COUCH_URL}/{COUCH_DB}/{doc_id}",
        auth=(COUCHDB_USER, COUCHDB_PASSWORD),
    )

    response.raise_for_status()
    return response.json()


def couch_put(doc: dict):
    response = requests.put(
        f"{COUCH_URL}/{COUCH_DB}/{doc['_id']}",
        auth=(COUCHDB_USER, COUCHDB_PASSWORD),
        json=doc,
    )

    response.raise_for_status()
    return response.json()

def update_aircon_status(**kwargs):

    doc = couch_get("aircon_status")

    for k, v in kwargs.items():
        doc[k] = v
        logging.info(v);

    doc["lastChanged"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    couch_put(doc)

def insert_dht_log(humidity, temperature):
    doc = {
        "type": "dht_log",
        "time": datetime.now(timezone.utc).isoformat(),
        "temperature": temperature,
        "humidity": humidity,
    }

    response = requests.post(
        f"{COUCH_URL}/{COUCH_DB}",
        auth=(COUCHDB_USER, COUCHDB_PASSWORD),
        json=doc,
    )

    response.raise_for_status()