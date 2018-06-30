# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 04:00:04 2018

@author: Harnick Khera github/hephyrius

this class deals with the signing of transactions as well as blockchain from the user side

using eliptic curve with SECP256k1 - AKA bitcoin type

currently the keys are generated based on date/time so can possibly be timed! need to add some randomness here!
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from base64 import b64decode,b64encode
from cryptography.hazmat.backends import default_backend
#import Main as hexDex
import Transaction as txn
import TransactionInput as ins
import TransactionOutput as outs


class Wallet():
     
     HashingFunction = ""
     PrivateKey = ""
     PublicKey = ""
     PEMPrivateKey = ""
     PEMPublicKey = ""
     UTXOs = dict()
     
     def __init__(self):
          
          self.HashingFunction = hashes.SHA256()
          self.PrivateKey = ec.generate_private_key(ec.SECP256K1, default_backend())
          self.PublicKey = self.PrivateKey.public_key()
          self.PEMPrivateKey  = self.PrivateKey.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
          self.PEMPublicKey = self.PublicKey.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
          self.UTXOs = dict()
     
     def getPublicKeyString(self):
          
          public  = self.PublicKey.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
          public = public.decode('utf-8')
          public = public.replace("-----BEGIN PUBLIC KEY-----\n", "")
          public = public.replace("-----END PUBLIC KEY-----\n", "")
         # public = public.replace("\n", "")
          return public
     
     def getPrivateKeyString(self):
          
          private  = self.PrivateKey.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
          private = private.decode('utf-8')
          private = private.replace("-----BEGIN EC PRIVATE KEY-----\n", "")
          private = private.replace("-----END EC PRIVATE KEY-----\n", "")
         # private = private.replace("\n", "")
          return private
     
     
     #get the balance of the wallet
     def getBalance(self, MainChain):
          
          self.UTXOs = dict()
          
          total = 0
          
          for i in MainChain.UTXOs:
               
               if MainChain.UTXOs[i]['Transaction'].Recipient == self.PEMPublicKey.decode() and MainChain.UTXOs[i]['Transaction'].Spent == False:
                    self.UTXOs[i] = {"Transaction":MainChain.UTXOs[i]['Transaction']}
                    total+= MainChain.UTXOs[i]['Transaction'].Value
          
          return total
     
     #function responsible for sending coins on the chain
     def SendFunds(self, _RecipientPublic, _Value, MainChain):
          
          if(self.getBalance(MainChain) < _Value):
               print("Not Enough Funds")
               return None
          
          #basically cycle thru the outputs, adding to the total and input list until done
          inputs = []
          total = 0
          
          for i in self.UTXOs:
               
               inputs.append(i)
               total += MainChain.UTXOs[i]['Transaction'].Value
               if total > _Value:
                    break
          
          transaction = txn.Transaction(self.PEMPublicKey, _RecipientPublic, _Value, 0, inputs)
          transaction.GenerateTransactionSignature(self.PrivateKey)
          
          #remove used UTXO from the wallet
          for i in inputs:
               self.UTXOs.pop(i)
          
          return transaction
