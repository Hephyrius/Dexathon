# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 23:27:05 2018

@author: Harnick Khera github/hephyrius


transaction class for dealing with transactions
"""

import UtilFunctions as utils
import TransactionInput as ins
import TransactionOutput as outs
#import Main as hexDex

class Transaction():
     
     TransactionHash = 0
     TransactionType = 0
     Sender = "0x0"
     Recipient = "0x0"
     Value = 0
     Signature = "0x0"
     TransactionInputs = []
     TransactionOutputs = []
     Sequence = 0
     MiscData = ""
     #constructor for a transaction
     def __init__(self, fromPublicKey, ToPublicKey, TransactionValue, TransactionType, TransactionInputData, MiscData=None):
          
          self.Sender = fromPublicKey
          self.Recipient = ToPublicKey
          self.Value = TransactionValue
          self.TransactionType = TransactionType
          self.TransactionInputs = TransactionInputData
          self.TransactionOutputs = []
          self.Signature = "0x0"
          self.Sequence = 0
          self.TransactionHash = "0x0"
          self.MiscData = MiscData
     
     #get a transaction hash for the transaction
     def CalculateHash(self):
          #increment the sequence count
          #self.Sequence += 1
          hashingData = str(self.Sender)+ "_" +str(self.Recipient) + "_" + str(self.Value) + "_" + str(self.TransactionType) + "_" + str(self.Sequence) 
          return utils.UtilFunctions.applySha256(utils.UtilFunctions, hashingData)
     
     #sign the transaction and generate the transaction sig
     def GenerateTransactionSignature(self, PrivateKey):
          Data = str(self.Sender)+ "_" +str(self.Recipient) + "_" + str(self.Value) + "_" + str(self.TransactionType) + "_" + str(self.Sequence)
          Data = str.encode(Data)
          self.Signature = utils.UtilFunctions.ApplyECDSignature(PrivateKey, Data)
          
     #verify the transactions signature
     def VerifyTransactionSignature(self):
          Data = str(self.Sender)+ "_" +str(self.Recipient) + "_" + str(self.Value) + "_" + str(self.TransactionType) + "_" + str(self.Sequence)
          Data = str.encode(Data)
          return utils.UtilFunctions.verifyECDSignature(self.Sender, Data, self.Signature)
     
     def ProcessTransaction(self, MainChain):
          
          #check for tampering
          if self.VerifyTransactionSignature() == False:
               
               print("Unable to verify Transaction")
               return False
          
          if self.TransactionType == 0:
               
               #check all UTXOs on the chain
               for i in range(len(self.TransactionInputs)):
                    
                    inp = ins.TransactionInput(self.TransactionInputs[i])
                    inp.UTXO = MainChain.UTXOs[self.TransactionInputs[i]]['Transaction']
                    self.TransactionInputs[i] = inp
                    
               #check that the transaction has a valid value - might remove this when we add extra currencies
               if self.GetInputsValue() < MainChain.MinimumTransactionValue:
                    
                    print("Value of transaction too low")
                    return False
               
               #calculate the order hash and the total left from the input transactions
               _LeftOverValue = self.GetInputsValue() - self.Value
               self.TransactionHash = self.CalculateHash()
               
               #create the transaction outputs and add them to the output list
               self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, _LeftOverValue, self.TransactionHash, self.TransactionType))
               self.TransactionOutputs.append(outs.TransactionOutput(self.Recipient, self.Value, self.TransactionHash, self.TransactionType))
               
               #add the transactions to the main chain UTXO list
               for i in self.TransactionOutputs:
                    MainChain.UTXOs[i.Id] = {'Transaction':i}
               
               #remove spent transactions
               for i in self.TransactionInputs:
                    if i.UTXO is None:
                         continue
                    MainChain.UTXOs[i.TransactionOutputId]['Transaction'].Spent = True
                    MainChain.UTXOs.pop(i.TransactionOutputId, None)
               
               return True
          
          #this type creates a new coin.
          if self.TransactionType == 1:
               
               fee = 100
               
               #check all UTXOs on the chain
               for i in range(len(self.TransactionInputs)):
                    
                    inp = ins.TransactionInput(self.TransactionInputs[i])
                    inp.UTXO = MainChain.UTXOs[self.TransactionInputs[i]]['Transaction']
                    self.TransactionInputs[i] = inp
                    
               #check that the transaction has a valid value, IE the value must be above the fee
               if self.GetInputsValue() < 100:
                    
                    print("Inputs are lower than fees")
                    return False
               
               if self.Value < 100:
                    print("Transaction value less than fees")
                    return False
               
               #Checks to prevent bad things from happening
               newCoinData = self.MiscData
               
               try:
                    if newCoinData == None:
                         print("No Arguments Given")
                         return False
                    
                    if type(newCoinData) != type(dict()):
                         print("Coin parameters not given in correct type")
                         return False
                         
                    if type(newCoinData['CoinName']) != type("") or len(newCoinData['CoinName']) < 1:
                         print("Coin Name not given correctly")
                         return False
                    
                    if type(newCoinData['Symbol']) != type("") or len(newCoinData['Symbol']) > 6 or len(newCoinData['Symbol']) < 1:
                         print("Coin Symbol not given correctly")
                         return False
                    
                    if type(newCoinData['Supply']) != type(0) or newCoinData['Supply'] <= 0:
                         print("Coin Supply Invalid")
                         return False
               except Exception as e:
                    print("Error processing coin creation data: " + e)
                    return False
               
               CoinHash = utils.UtilFunctions.applySha256(utils.UtilFunctions, newCoinData['Symbol']+"_"+newCoinData['CoinName']+"_"+str(newCoinData['Supply']))
               if CoinHash in MainChain.AlternativeCoins:
                    print("Coin Hash collision try different parameters")
                    return False
               
               #calculate the order hash and the total left from the input transactions
               _LeftOverValue = self.GetInputsValue() - fee
               self.TransactionHash = self.CalculateHash()
               
               #create the transaction outputs, these outputs deduct from the balance AND burn the fees -- Burning could be replaced with POS incentives?
               self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, _LeftOverValue, self.TransactionHash, 0))
               self.TransactionOutputs.append(outs.TransactionOutput("0x0", fee, self.TransactionHash, 0))
               
               #this is our genesis transaction for the new coin!
               self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, newCoinData['Supply'], self.TransactionHash, 2, CoinHash))
               
               #add the transactions to the main chain UTXO list
               for i in self.TransactionOutputs:
                    MainChain.UTXOs[i.Id] = {'Transaction':i}
               
               MainChain.AlternativeCoins.append(CoinHash)
               
               #remove spent transactions
               for i in self.TransactionInputs:
                    if i.UTXO is None:
                         continue
                    MainChain.UTXOs[i.TransactionOutputId]['Transaction'].Spent = True
                    MainChain.UTXOs.pop(i.TransactionOutputId, None)
               
               return True
     
     def GetInputsValue(self):
          
          _total = 0
          
          for i in self.TransactionInputs:
               if i.UTXO is None:
                    continue
               _total += i.UTXO.Value
               
          
          return _total
     
     
     def GetOutputsValue(self):
          
          _total = 0

          for i in self.TransactionOutputs:

               _total += i.Value
               

          return _total
          
          
          
          
          
          
          
          
          
          
          
          
          