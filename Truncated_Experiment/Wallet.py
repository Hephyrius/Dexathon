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
               
               if MainChain.UTXOs[i]['Transaction'].Recipient == self.PEMPublicKey.decode() and MainChain.UTXOs[i]['Transaction'].Frozen == False and MainChain.UTXOs[i]['Transaction'].TransactionType == 0:
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
          
          transaction = txn.Transaction(self.PEMPublicKey.decode(), _RecipientPublic, _Value, 0, inputs)
          transaction.GenerateTransactionSignature(self.PrivateKey)
          
          #remove used UTXO from the wallet
          for i in inputs:
               self.UTXOs.pop(i)
          
          return transaction
     
     #function responsible for sending tokens on the chain
     def SendToken(self, _RecipientPublic, _Value, Coin, MainChain):
          
          if(self.GetTokenBalance(MainChain, Coin) < _Value):
               print("Not Enough Funds")
               return None
          
          #basically cycle thru the outputs, adding to the total and input list until done
          inputs = []
          total = 0
          
          for i in self.UTXOs:
               if MainChain.UTXOs[i]['Transaction'].TransactionType == 2 and MainChain.UTXOs[i]['Transaction'].Data == Coin:
                    inputs.append(i)
                    total += MainChain.UTXOs[i]['Transaction'].Value
                    if total > _Value:
                         break
          
          MiscData = {"CoinHash":Coin}
          transaction = txn.Transaction(self.PEMPublicKey.decode(), _RecipientPublic, _Value, 2, inputs, MiscData)
          transaction.GenerateTransactionSignature(self.PrivateKey)
          
          #remove used UTXO from the wallet
          for i in inputs:
               self.UTXOs.pop(i)
          
          return transaction
     
     #function responsible for burning tokens on the chain
     def BurnToken(self, _Value, Coin, MainChain):
          
          if(self.GetTokenBalance(MainChain, Coin) < _Value):
               print("Not Enough Funds")
               return None
          
          #basically cycle thru the outputs, adding to the total and input list until done
          inputs = []
          total = 0
          
          for i in self.UTXOs:
               if MainChain.UTXOs[i]['Transaction'].TransactionType == 2 and MainChain.UTXOs[i]['Transaction'].Data == Coin:
                    inputs.append(i)
                    total += MainChain.UTXOs[i]['Transaction'].Value
                    if total > _Value:
                         break
          
          MiscData = {"CoinHash":Coin}
          transaction = txn.Transaction(self.PEMPublicKey.decode(), "0x0", _Value, 3, inputs, MiscData)
          transaction.GenerateTransactionSignature(self.PrivateKey)
          
          #remove used UTXO from the wallet
          for i in inputs:
               self.UTXOs.pop(i)
          
          return transaction
     
     #function used in wallet to create a new coin
     def CreateNewCoin(self, MainChain, CoinName, CoinSymbol, CoinSupply):
          
          if(self.getBalance(MainChain) < 100):
               print("Not Enough Funds")
               return None
          
          #basically cycle thru the outputs, adding to the total and input list until done
          inputs = []
          total = 0
          
          for i in self.UTXOs:
               
               if MainChain.UTXOs[i]['Transaction'].TransactionType == 0:
                    inputs.append(i)
                    total += MainChain.UTXOs[i]['Transaction'].Value
                    if total >= 100:
                         break
          
          MiscData = {"CoinName":CoinName, "Symbol":CoinSymbol, "Supply":CoinSupply}
          transaction = txn.Transaction(self.PEMPublicKey.decode(), "0x0", 100, 1, inputs, MiscData)
          transaction.GenerateTransactionSignature(self.PrivateKey)
          
          #remove used UTXO from the wallet
          for i in inputs:
               self.UTXOs.pop(i)
          
          return transaction
      
     #get the balance of the wallet
     def GetTokenBalance(self, MainChain, Coin):
          
          self.UTXOs = dict()
          
          total = 0
          
          for i in MainChain.UTXOs:
               
               if MainChain.UTXOs[i]['Transaction'].Recipient == self.PEMPublicKey.decode() and MainChain.UTXOs[i]['Transaction'].TransactionType == 2 and MainChain.UTXOs[i]['Transaction'].Data == Coin:
                    self.UTXOs[i] = {"Transaction":MainChain.UTXOs[i]['Transaction']}
                    total+= MainChain.UTXOs[i]['Transaction'].Value
          
          return total
     
          #get the balance of the wallet
     def GetSpentableTokenBalance(self, MainChain, Coin):
          
          self.UTXOs = dict()
          
          total = 0
          
          for i in MainChain.UTXOs:
               
               if MainChain.UTXOs[i]['Transaction'].Recipient == self.PEMPublicKey.decode() and MainChain.UTXOs[i]['Transaction'].TransactionType == 2 and MainChain.UTXOs[i]['Transaction'].Data == Coin and MainChain.UTXOs[i]['Transaction'].Frozen == False:
                    self.UTXOs[i] = {"Transaction":MainChain.UTXOs[i]['Transaction']}
                    total+= MainChain.UTXOs[i]['Transaction'].Value
          
          return total
     
     #freezetokens
     def FreezeUnfreezeTokens(self, _Value, Coin, FreezeState, MainChain):
          if FreezeState == True:
               if(self.GetTokenBalance(MainChain, Coin) < _Value):
                    print("Not Enough Funds")
                    return None
               
               #basically cycle thru the outputs, adding to the total and input list until done
               inputs = []
               total = 0
               
               for i in self.UTXOs:
                    if MainChain.UTXOs[i]['Transaction'].TransactionType == 2 and MainChain.UTXOs[i]['Transaction'].Data == Coin and MainChain.UTXOs[i]['Transaction'].Frozen == False:
                         inputs.append(i)
                         total += MainChain.UTXOs[i]['Transaction'].Value
                         if total > _Value:
                              break
               
               MiscData = {"CoinHash":Coin, "Freeze":FreezeState}
               transaction = txn.Transaction(self.PEMPublicKey.decode(), "0x0", _Value, 4, inputs, MiscData)
               transaction.GenerateTransactionSignature(self.PrivateKey)
               
               #remove used UTXO from the wallet
               for i in inputs:
                    self.UTXOs.pop(i)
                    
          else:
               if(self.GetTokenBalance(MainChain, Coin) < _Value):
                    print("Not Enough Funds to unfreeze")
                    return None
               
               #basically cycle thru the outputs, adding to the total and input list until done
               inputs = []
               total = 0
               
               for i in self.UTXOs:
                    if MainChain.UTXOs[i]['Transaction'].TransactionType == 2 and MainChain.UTXOs[i]['Transaction'].Data == Coin and MainChain.UTXOs[i]['Transaction'].Frozen == True:
                         inputs.append(i)
                         total += MainChain.UTXOs[i]['Transaction'].Value
                         if total > _Value:
                              break
               
               MiscData = {"CoinHash":Coin, "Freeze":FreezeState}
               transaction = txn.Transaction(self.PEMPublicKey.decode(), "0x0", _Value, 4, inputs, MiscData)
               transaction.GenerateTransactionSignature(self.PrivateKey)
               
               #remove used UTXO from the wallet
               for i in inputs:
                    self.UTXOs.pop(i)
          
          return transaction
     
     #function to create buy and sell orders
     def CreateOrder(self, CoinHash, Rate, Total, BuyFlag, MainChain):
          
          if BuyFlag == True:
               
               val = Total*Rate
               
               if self.getBalance(MainChain) < val:
                    
                    print("not enough native coin to create order")
                    return None               
          

               #basically cycle thru the outputs, adding to the total and input list until done
               inputs = []
               total = 0
               
               for i in self.UTXOs:
                    
                    inputs.append(i)
                    total += MainChain.UTXOs[i]['Transaction'].Value
                    if total > val:
                         break
               
               MiscData = {"CoinHash":CoinHash, "Rate":Rate, "Total":Total, "BuyFlag":BuyFlag}
               transaction = txn.Transaction(self.PEMPublicKey.decode(), "0x0", 0, 5, inputs, MiscData)
               transaction.GenerateTransactionSignature(self.PrivateKey)
               
               return transaction
          
          else:
               
               val = Total
               
               if self.GetTokenBalance(MainChain, CoinHash) < val:
                    
                    print("not enough Tokens to trade order")
                    return None               
               

               #basically cycle thru the outputs, adding to the total and input list until done
               inputs = []
               total = 0
               
               for i in self.UTXOs:
                    if MainChain.UTXOs[i]['Transaction'].TransactionType == 2 and MainChain.UTXOs[i]['Transaction'].Data == CoinHash:
                         inputs.append(i)
                         total += MainChain.UTXOs[i]['Transaction'].Value
                         if total > val:
                              break
               
               MiscData = {"CoinHash":CoinHash, "Rate":Rate, "Total":Total, "BuyFlag":BuyFlag}
               transaction = txn.Transaction(self.PEMPublicKey.decode(), "0x0", 0, 5, inputs, MiscData)
               transaction.GenerateTransactionSignature(self.PrivateKey)
          
               return transaction
               
               
               
     
     
     
     
     
     
     
     
     
     
     
     
