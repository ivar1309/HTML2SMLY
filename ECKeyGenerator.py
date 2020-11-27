import ecdsa
import os
import base58check
from ecdsa.util import string_to_number, number_to_string

_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_b = 0x0000000000000000000000000000000000000000000000000000000000000007
_a = 0x0000000000000000000000000000000000000000000000000000000000000000
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
generator_secp256k1 = ecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _r)


class ECKeyGenerator:
    def __init__(self):
        self.generator = generator_secp256k1
    
    def genRandomPrivKey(self):
        self.secret = self.randomSecret()
        self.point = self.secret * self.generator

    def setPrivKey(self, wifCompressedKey):
        try:
            key = base58check.b58decode(wifCompressedKey)[1:-5].hex()
        except ValueError:
            key = wifCompressedKey
        self.secret = int(key, 16)
        self.point = self.secret * self.generator

    def printPrivKey(self):
        print(f"Private Key: {hex(self.secret)[2:]}")

    def getPrivKey(self):
        return hex(self.secret)[2:]

    def randomSecret(self):
        convert_to_int = lambda array: int(array.hex(), 16)
        # Collect 256 bits of random data from the OS's cryptographically secure random generator
        byte_array = os.urandom(32)
        return convert_to_int(byte_array)

    def getPubkey(self):
        if self.point.y() & 1:
            key = '03' + '{:064x}'.format(self.point.x())
        else:
            key = '02' + '{:064x}'.format(self.point.x())
        return key

    def getPubkeyUncompressed(self):
        key = '04' + '{:064x}'.format(self.point.x()) + '{:064x}'.format(self.point.y())
        return key

    def privKeySign(self, hash):
        pk = hex(self.secret)[2:]
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(pk), curve=ecdsa.SECP256k1)
        return sk.sign_digest(hash, sigencode=ecdsa.util.sigencode_der)

if __name__ == "__main__":
    ECKG = ECKeyGenerator()
    ECKG.genRandomPrivKey()
    ECKG.printPrivKey()
    print(f"Public Key: {ECKG.getPubkey()}")
    print(f"Public Key Uncompressed: {ECKG.getPubkeyUncompressed()}")