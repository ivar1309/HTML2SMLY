import re
import os
import sys
import time
import htmlmin
from dotenv import load_dotenv
import Transaction as Tx
import Api
import Address

def chrToPrintableAscii(ch):
    # subtract 31 to keep the range between 1 and 95
    return "{:02d}".format(ord(ch) - 31)

def printableAsciiToChr(code):
    return chr(code + 31)

def readWebpage(file):
    html = ""
    with open(file) as f:
        html = "".join(f.readlines())
    return htmlmin.minify(html, remove_empty_space=True)

def chopHtmlIntoChunksOfFourChars(html):
    return re.findall(".{1,4}", html)

def encodeCharsAsAmount(chrStr):
    # ["34","35","36","37"]
    asciiArr = [str(chrToPrintableAscii(ch)) for ch in chrStr]
    # encode 4 chars as "0.########" and 3 chars as "0.######" and so on.
    amount = "0." + "".join(asciiArr)
    # 0.34353637
    return float(amount)


if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) > 1:
        htmlFile = sys.argv[1]
    else:
        htmlFile = "index.html"

    signingPrivKey = os.getenv("signingPrivKey")
    sendingAddress = os.getenv("sendingAddress")
    recievingInfo = Address.generateKeysAndAddress()
    htmlArr = chopHtmlIntoChunksOfFourChars(readWebpage(htmlFile))
    encodedHtml = [encodeCharsAsAmount(chunk) for chunk in htmlArr]
    alreadyUsedInputs = []

    # For every four characters we get the unspent SMLY from the api
    # and calculate the wait time based on the number of utxos recieved.
    # Then we proceed  going through the sorted list of utxos checking if
    # we have one that is greater then the encoded amount. Lastly we 
    # calculate the fee and change and then create, sign and send the
    # transaction.
    for j, chunk in enumerate(encodedHtml):
        utxos = Api.getUtxo(sendingAddress)
        utxos = sorted(utxos, key=lambda utxo: utxo["amount"])
        print(f"utxo #: {len(utxos)}")
        waitTime = 60/len(utxos)
        outputs = []
        chunkAmount = float(chunk)
        for i, utxo in enumerate(utxos):
            if utxo["txid"] in alreadyUsedInputs:
                print(f"{utxo['txid']} already spent")
                continue
            utxoAmount = float(utxo["amount"])
            if chunkAmount < utxoAmount:
                inputTxid = utxo["txid"]
                vout = utxo["vout"]
                scriptPubKey = utxo["scriptPubKey"]
                # fee will be 10% of the difference but at most 1 SMLY
                fee = min((utxoAmount - chunkAmount) * 0.1, 1)
                change = utxoAmount - chunkAmount - fee
                outputs.append({"address": recievingInfo["address"], "amount": chunkAmount})
                outputs.append({"address": sendingAddress, "amount": change})
                signedTx = Tx.createAndSignTransaction(signingPrivKey, inputTxid, vout, scriptPubKey, outputs, j + 1)
                txid = Tx.sendTransaction(signedTx)
                if "error" not in txid:
                    alreadyUsedInputs.append(utxo["txid"])
                print(f"{utxo['txid']} - {utxoAmount} -- chunk: {chunkAmount}")
                print(f"{htmlArr[j]} encoded as {chunk}")
                print(f"txid: {txid['txid']}")
                #utxos.pop(i)
                break
        print(f"will wait for {int(waitTime)} s")
        time.sleep(waitTime)
    
    print(f"HTML is encoded into SMLY and sent to this address: {recievingInfo['address']}")
    print(f"To spend them and therefore erase the HTML use this private key")
    print(f"Private Key: {recievingInfo['privKey']}")


    #for i in range(0, len(htmlArr)):
    #    print(f"{htmlArr[i]} as {encodedHtml[i]}")