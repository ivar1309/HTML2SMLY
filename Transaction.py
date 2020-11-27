import struct
import hashlib
from decimal import *
import Api
import Address
import ECKeyGenerator

def getTxidLittleEndian(txid):
    return bytes.fromhex(txid)[::-1].hex()

def calculateSatoshis(amount):
    # set the decimal precision to 8,
    # using Decimal module instead of float
    # to avoid rounding errors. 
    getcontext().prec = 8
    amountInSatoshis = int(Decimal(amount) * 100000000)
    return struct.pack("<Q", amountInSatoshis).hex()

def formatOutput(output):
    # scriptPubKey = OP_DUP OP_HASH160 hash_len pubkey_hash OP_EQUALVERIFY OP_CHECKSIG
    scriptPubKey = "76a914" + Address.getPubKeyHash(output["address"]) + "88ac"
    scriptLength = "{:02x}".format(len(bytes.fromhex(scriptPubKey)))
    return calculateSatoshis(output["amount"]) + scriptLength + scriptPubKey

def createRawTransaction(inputTxid, vout, signature, outputs, sequence=4294967295):
    tx = "01000000" # version
    tx += "01" # number of inputs
    tx += getTxidLittleEndian(inputTxid) # input-txid
    tx += struct.pack("<L", vout).hex() # vout
    tx += "{:02x}".format(len(bytes.fromhex(signature))) # signature length
    tx += signature # signature
    #tx += "ffffffff" # sequence
    tx += struct.pack("<L", sequence).hex()
    tx += "{:02x}".format(len(outputs)) # number of outputs
    tx += "".join([formatOutput(o) for o in outputs]) # outputs
    tx += "00000000" # locktime
    return tx

def createAndSignTransaction(privateKey, inputTxid, vout, scriptPubKey, outputs, sequence=4294967295):
    # steps from https://bitcoin.stackexchange.com/questions/3374/how-to-redeem-a-basic-tx
    # with http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html
    # as a reference
    ECKG = ECKeyGenerator.ECKeyGenerator()
    ECKG.setPrivKey(privateKey)
    txToSign = createRawTransaction(inputTxid, vout, scriptPubKey, outputs, sequence)
    txToSign += "01000000" # hash type
    hashedTx = hashlib.sha256(hashlib.sha256(bytes.fromhex(txToSign)).digest()).digest()
    signature = ECKG.privKeySign(hashedTx).hex()
    signature += "01" # hash type
    pubKey = ECKG.getPubkey()
    scriptSig = "{:02x}".format(len(bytes.fromhex(signature)))
    scriptSig += signature
    scriptSig += "{:02x}".format(len(bytes.fromhex(pubKey)))
    scriptSig += pubKey
    signedTx = createRawTransaction(inputTxid, vout, scriptSig, outputs, sequence)
    return signedTx

def sendTransaction(tx):
    return Api.sendTx(tx)


if __name__ == "__main__":
    inputTxid = "faaa6031333067b24d211b13713c13417485e3a319ec278a71b75bc2cadee976"
    scriptPubKey = "76a91410c0b281ac1c19254e4d4e0c3472050e0f97837f88ac"
    privateKey = "Piwan5qawF6ZBaUpHqDgCMvLkwjktuybrUMiVrxn2Q67VEDYmNP5"
    vout = 0
    signature = ""
    outputs = [{"address":"BEd9V6vQ1P8W4oBacKKanq5Yif8MzJv3sS", "amount": 121}]
    rawTx = createRawTransaction(inputTxid, vout, "", outputs)
    signedTx = createAndSignTransaction(privateKey, inputTxid, vout, scriptPubKey, outputs)
    print(f"rawTX: {rawTx}")
    print(f"signedTX: {signedTx}")