import requests
import config
import math
import json

def dead_response(message="Invalid Request", rid=config.rid):
    return {"error": {"code": 404, "message": message}, "id": rid}

def response(result, error=None, rid=config.rid):
    return {"error": error, "id": rid, "result": result}

def make_request(method, params=[]):
    headers = {"content-type": "text/plain;"}
    data = json.dumps({"id": config.rid, "method": method, "params": params})

    try:
        return requests.post(config.endpoint, headers=headers, data=data).json()
    except Exception:
        return dead_response()

def getaddressbalance(address: str):
    headers = {"content-type": "text/plain;"}
    try:
        result = requests.get(config.blockbook + 'api/v2/address/' + address, headers=headers).json()
        return {"error": None, "id": config.rid, "result": {"balance": result['balance'], "received": result['totalReceived']}}
    except Exception:
        return dead_response()

def getaddressutxos(address: str, amount: int = -1):
    headers = {"content-type": "text/plain;"}
    try:
        result = requests.get(config.blockbook + 'api/v2/utxo/' + address + '?confirmed=true', headers=headers).json()
        utxos = []
        value = 0
        for utxo in reversed(result):
            value += int(utxo["value"])
            tx_data = make_request("getrawtransaction", [utxo["txid"], True])
            utxos.append({
                "txid": utxo["txid"],
                "index": utxo["vout"],
                "script": tx_data["result"]["vout"][utxo["vout"]]["scriptPubKey"]["hex"],
                "value": int(utxo["value"]),
                "height": utxo["height"]
            })
            if amount >= 0 and value >= amount:
                break
        return {"error": None, "id": config.rid, "result": utxos}
    except Exception:
        return dead_response()

def getaddresstxids(address: str):
    headers = {"content-type": "text/plain;"}
    try:
        result = requests.get(config.blockbook + 'api/v2/address/' + address + '?details=txids', headers=headers).json()
        return {"error": None, "id": config.rid, "result": {"tx": result["txids"], "txcount": len(result["txids"])}}
    except Exception:
        return dead_response()

def reward(height):
    halvings = height // 1051200

    if halvings >= 64:
        return 0

    return int(satoshis(50) // (2 ** halvings))

def supply(height):
    reward = satoshis(50)
    halvings = 1051200
    halvings_count = 0
    supply = reward

    if height > 0:
        while height > halvings:
            total = halvings * reward
            reward = reward / 2
            height = height - halvings
            halvings_count += 1

            supply += total

        supply = supply + height * reward
    else:
        supply = 0

    return {
        "halvings": int(halvings_count),
        "supply": int(supply)
    }

def satoshis(value):
    return math.ceil(value * math.pow(10, 8))

def amount(value):
    return round(value / math.pow(10, 8), 8)
