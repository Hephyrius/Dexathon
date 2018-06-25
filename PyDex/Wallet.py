# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 04:00:04 2018

@author: Harnick Khera github/hephyrius


this class deals with the signing of transactions as well as blockchain from the user side

using eliptic curve with SECP256k1 - AKA bitcoin type
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from base64 import b64decode,b64encode
from cryptography.hazmat.backends import default_backend

class Wallet():
     
     HashingFunction = ""
     PrivateKey = ""
     PublicKey = ""
     PEMPrivateKey = ""
     PEMPublicKey = ""
     
     def __init__(self):
          
          self.HashingFunction = hashes.SHA256()
          self.PrivateKey = ec.generate_private_key(ec.SECP256K1, default_backend())
          self.PublicKey = self.PrivateKey.public_key()
          self.PEMPrivateKey  = self.PrivateKey.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
          self.PEMPublicKey = self.PublicKey.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
 

#basic testing         
wallet = Wallet()
print(wallet.PEMPrivateKey.decode('utf-8'))
print(wallet.PEMPrivateKey.decode('utf-8'))

#init two values to test for unique keys
a = wallet.PEMPrivateKey.decode('utf-8')
wallet2 = Wallet()
b = wallet2.PEMPrivateKey.decode('utf-8')

#check if a and b are different
print(a==b)
print(a==a)
print(b==b)