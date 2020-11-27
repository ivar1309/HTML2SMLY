import time
import math
import hashlib
import base58check
import ECKeyGenerator

# New address is created by the process described
# in the book Mastering Bitcoin by Antonopoulos
def getNewAddress(pubkey):
    # Version prefix for SMLY
    version_prefix = b'\x19'
    pubkeybytes = bytes.fromhex(pubkey)
    sha256 = hashlib.sha256(pubkeybytes).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256)
    payload = ripemd160.digest()
    checksum = hashlib.sha256(hashlib.sha256(version_prefix + payload).digest()).digest()[0:4]
    return base58check.b58encode(version_prefix + payload + checksum)

def getPubKeyHash(address):
    return base58check.b58decode(address)[1:-4].hex()

def generateKeysAndAddress():
    ECKG = ECKeyGenerator.ECKeyGenerator()
    ECKG.genRandomPrivKey()
    pubkey = ECKG.getPubkey()
    address = getNewAddress(pubkey)
    ECKG.printPrivKey()
    return {"privKey": ECKG.getPrivKey(), "pubKey": pubkey, "address": address}


if __name__ == "__main__":
    ECKG = ECKeyGenerator.ECKeyGenerator()
    ECKG.genRandomPrivKey()
    pubkey = ECKG.getPubkey()
    address = getNewAddress(pubkey)
    ECKG.printPrivKey()
    print(f"Public Key: {pubkey}")
    print(f"Address: {address}")