# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 04:00:04 2018

@author: Khera
"""

#requries pip install crypto
from crypto.PublicKey import RSA

class Wallet():
     
     PrivateKey = ""
     PublicKey = ""
     
     def __init__(self):
          
          self.PrivateKey = RSA.generate(2048)
          self.PublicKey = self.PrivateKey.publickey()
          
          