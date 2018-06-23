# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 04:00:04 2018

@author: Khera

this class deals with the signing of transactions as well as blockchain from the user side
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class Wallet():
     
     PrivateKey = ""
     PEMKey = ""
     PublicKey = ""
     
     def __init__(self):
          
          self.PrivateKey = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
          self.PublicKey = self.PrivateKey.public_key().public_bytes(serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)
          self.PEMKey  = self.PrivateKey.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
          
          
wallet = Wallet()
print(wallet.PEMKey.decode('utf-8'))