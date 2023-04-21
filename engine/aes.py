
# by Jakub Grzana

# 16byte key means 2^128 possibilities, over 10^38. According to internet, it's still safe.
# Encrypted data is bytearray, can be easily saved to file
# In encrypted data, IV key and hash (sha256) of data is stored, and validity of this data is checked on decryption
# Also i've 0 education in safety and encryption. I hope im doing it right.

import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import pickle
import hashlib
import log as Log
from constants import SALT_FILENAME

####################################################################################################################

def LoadOrGenerateKey(filepath, bytelength=32):
    if os.path.isfile(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    else:
        Log.Expected.Write(RuntimeError(f"Cannot load key from {filepath}, generating new one..."))
        key = GenerateKey(bytelength)
        with open(filepath, "wb") as f:
            pickle.dump(key, f, -1)
        return key

SALT = None

def LoadSalt():
    global SALT
    SALT = LoadOrGenerateKey(SALT_FILENAME)
    return SALT

def GenerateKey(bytelength=16):
    if bytelength not in {16,24,32}: raise RuntimeError("Incorrect bytelength for AES encryption: " + str(bytelength))
    return get_random_bytes(bytelength)

def PasswdToKey(passwd, bytelength=16):
    salt = LoadSalt()
    key = PBKDF2(passwd, salt, dkLen=bytelength)
    return key

def Encrypt(key, var):
    iv = GenerateKey(16)
    coder = AES.new(key, AES.MODE_CFB, iv=iv)
    data = pickle.dumps(var, -1)
    hash = hashlib.sha256(data).hexdigest()
    cipher = coder.encrypt(data)
    dump = pickle.dumps((iv, cipher, hash), -1)
    return dump
    
def Decrypt(key, dump):
    (iv, cipher, hash) = pickle.loads(dump)
    coder = AES.new(key, AES.MODE_CFB, iv=iv)
    data = coder.decrypt(cipher)
    if hashlib.sha256(data).hexdigest() != hash:
        raise RuntimeError("Incorrect hash, which most likely means tampering with cipher or incorrect decryption")
    var = pickle.loads(data)
    return var

####################################################################################################################