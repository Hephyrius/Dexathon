# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 02:56:37 2018

@author: Harnick Khera github/hephyrius


class is responsible for utility functions such as hashing

"""
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

import hashlib


class UtilFunctions:
     
     
     def applySha256(self, _inputData):
          calculatedhash = hashlib.sha256(_inputData.encode())
          hex_dig = calculatedhash.hexdigest()
          
      #    return calculatedhash, hex_dig
          return hex_dig
     
     #apply Private key to the transactiondata
     def ApplyECDSignature(PrivateKey, Data):
          Signature = PrivateKey.sign( Data, ec.ECDSA(hashes.SHA256()))
          return Signature
     
     
     #verify a signature using a public key, if no error is thrown we get a bool of true, else we get a false
     def verifyECDSignature(Publickey, Data, Signature):
          
          try:
               Publickey.verify(Signature, Data, ec.ECDSA(hashes.SHA256()))
               return True
          except Exception as e:
               #print(e)
               return False
     
     
     #calculate merkel root - not advanced but simple
     def GetMerkelRoot(transactions):
          
          count = len(transactions)
          
          previousLayer = []
          
          for i in transactions:
               previousLayer.append(i.TransactionHash)
          
          
          while count > 1:
               treeLayer = []
               
               for i in range(1,len(previousLayer)):
                    treeLayer.append(applySha256(previousLayer[i-1]+previousLayer[i]))
               
               count = len(treeLayer)
               previousLayer = treeLayer
          
          root = ""
          if len(root) == 1:
               root = treeLayer[0]
          
          return root












