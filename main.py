# %%
from fastapi import FastAPI
import requests, json
import couchdb
import datetime
import logging
from model import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

# %%
app = FastAPI()
DEFAULT_TIMEOUT = 3

@app.get('/health')
def health():
    return {'status': 'ok'}


# %%
def get_url(uri= ""):
    return "http://192.168.0.7" + "/" + uri.lstrip("/")

# %%
@app.get("/dht/hat")
def get_hat():
    url = get_url("hat")
    response = requests.get(url=url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()

    data = response.json()
    return data

# %%
@app.post(path="/ir/decode")
def request_ir_decode(timeout=5000):
    url = get_url("ir/decode")
    response = requests.post(url, {"timeout": timeout})
    response.raise_for_status()
    return json.loads(response.text)


# %%
@app.get("/ir/result_decode")
def get_ir_decode():
    url = get_url(uri="ir/result_decode")
    response = requests.get(url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return json.loads(response.text)

# %%
@app.post(path="/ir/poweroff")
def ir_power_off():
    url = get_url(uri="ir/poweroff")
    response = requests.post(url=url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    couchdb.update_aircon_status(power=False)
    return {
            "status": "ok",
            "message": response.text
        }

# %%
@app.post(path="/ir/poweron")
def ir_power_on():
    url = get_url(uri="ir/poweron")
    response = requests.post(url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    couchdb.update_aircon_status(power=True, temperature=24, windDahyeon=4)
    return {
            "status": "ok",
            "message": response.text
        }

# %%
@app.post("/ir/temperature")
def ir_adjust_temperature(req: TemperatureRequest):
    temp = req.temp
    url = get_url(uri="ir/temperature")
    response = requests.post(url=url, data={"value": temp}, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    couchdb.update_aircon_status(temperature=temp)
    return {
            "status": "ok",
            "message": response.text
        }

# %%
@app.post("/ir/wind")
def ir_adjust_wind(req: WindRequest):
    wind = req.wind
    url = get_url(uri="ir/wind")
    response = requests.post(url=url, data={"value": wind}, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    logging.info(f"wind adjust:windDahyeon={str(wind)}")
    couchdb.update_aircon_status(windDahyeon=wind)
    return {
            "status": "ok",
            "message": response.text
        }

# %%
@app.get(path="/ir/status")
def ir_status():
    url = get_url(uri="ir/status")
    response = requests.get(url=url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return json.loads(response.text)

# %%
# startup - 주기적으로 온/습도 저장
import threading
import time
DHT_SAVE_INTERVAL_SEC = 60 * 5
def dht_logger():
    while True:
        try:
            data = get_hat()
            couchdb.insert_dht_log(humidity=data['humidity'], temperature=data["temperature"])
            logging.info(str(datetime.datetime.now()) + " 온/습도 로깅 성공, " + str(data))
        except Exception as e:
            logging.error(e)
        time.sleep(DHT_SAVE_INTERVAL_SEC)

@app.on_event("startup")
def startup():
    threading.Thread(
        target = dht_logger,
        daemon=True,
    ).start()
    logging.info("온/습도 로거 시작")


# %%
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
