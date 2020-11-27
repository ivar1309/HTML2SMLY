from decimal import *
from flask import Flask
import requests

def printableAsciiToChar(code):
    return chr(int(code) + 31)

def decodeAmountAsChars(amount):
    getcontext().prec = 8
    chrStr = str(int(Decimal(amount) * 100000000))
    # zero pad chrStr if needed to get the length 8
    chrStr = (8 - len(chrStr)) * "0" + chrStr
    chrArr = [chrStr[i:i+2] for i in range(0, len(chrStr), 2)]
    return "".join(map(printableAsciiToChar, chrArr))

app = Flask(__name__)

@app.route('/')
def hello_world():
    return ''

@app.route('/addr/<string:address>')
def show_html(address):
    res = requests.get(f"https://blocks.smileyco.in/api/addr/{address}/utxo")
    utxos = res.json()
    htmlEncoded = []
    for utxo in utxos:
        res = requests.get(f"https://blocks.smileyco.in/api/tx/{utxo['txid']}")
        tx = res.json()
        htmlEncoded.append({"amount": utxo["amount"], "sequence": tx["vin"][0]["sequence"]})
    htmlEncoded = sorted(htmlEncoded, key=lambda chunk: chunk["sequence"])
    output = "".join(decodeAmountAsChars(chunk["amount"]) for chunk in htmlEncoded)