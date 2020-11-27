import json
import subprocess
import requests

endpoint = "https://blocks.smileyco.in/api/"

def log(r):
    print(f"res: {r} - {r.status_code} - {r.text}")

def getUtxo(address):
    res = requests.get(endpoint + "addr/" + address + "/utxo")
    return json.loads(res.text)

def sendTx(rawtx):
    try:
        res = requests.post(endpoint + "tx/send", data={"rawtx": rawtx})
        if res.status_code == 200:
            jsonDecoded = json.loads(res.text)
        else:
            log(res)
            # if api endpoint returns an error, try sending through cli
            cmd = ["smileycoin-cli", "sendrawtransaction", rawtx]
            out = subprocess.run(cmd, capture_output=True, text=True)
            raw = out.stdout.strip()
            jsonDecoded = { "txid": raw }
            print("Transaction sent through CLI")
    except ValueError:
        log(res)
        jsonDecoded = { "error": True }
    except json.decoder.JSONDecodeError:
        log(res)
        jsonDecoded = { "error": True }
    except:
        print(f"Unknown error sending transaction")

    return jsonDecoded