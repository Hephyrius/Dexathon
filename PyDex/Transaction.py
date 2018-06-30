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
               
               CoinHash = utils.UtilFunctions.applySha256(utils.UtilFunctions, newCoinData['Symbol']+"_"+newCoinData['CoinName'])#+"_"+str(newCoinData['Supply']))
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
               MainChain.Markets.append(newCoinData)
               
               #remove spent transactions
               for i in self.TransactionInputs:
                    if i.UTXO is None:
                         continue

                    MainChain.UTXOs.pop(i.TransactionOutputId, None)
               
               return True
          
          #this sends created coins
          if self.TransactionType == 2:
               
               
               #Checks to prevent bad things from happening
               inputData = self.MiscData
               try:
                    if inputData == None:
                         print("No Arguments Given")
                         return False
                    
                    if type(inputData) != type(dict()):
                         print("Coin parameters not given in correct type")
                         return False
                         
                    if type(inputData['CoinHash']) != type("") or len(inputData['CoinHash']) < 1:
                         print("Coin Hash not given correctly")
                         return False
                    
                    if inputData['CoinHash'] not in MainChain.AlternativeCoins:
                         print("Coin not found")
                         return False
               except Exception as e:
                    print("Error processing coin creation data: " + e)
                    return False
               
               
               #check all UTXOs on the chain
               for i in range(len(self.TransactionInputs)):
                    #if MainChain.UTXOs[self.TransactionInputs[i]]['Transaction'].TransactionType == 2 and MainChain.UTXOs[self.TransactionInputs[i]]['Transaction'].Data == inputData['CoinHash']:
                         
                    inp = ins.TransactionInput(self.TransactionInputs[i])
                    inp.UTXO = MainChain.UTXOs[self.TransactionInputs[i]]['Transaction']
                    self.TransactionInputs[i] = inp
                    
               
               if self.GetInputsValue() < self.Value:
                    print("Trying to send token value more than amount owned")
                    return False
               
               #calculate the order hash and the total left from the input transactions
               _LeftOverValue = self.GetInputsValue() - self.Value
               self.TransactionHash = self.CalculateHash()
               
               #create the transaction outputs and add them to the output list
               self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, _LeftOverValue, self.TransactionHash, 2, inputData['CoinHash']))
               self.TransactionOutputs.append(outs.TransactionOutput(self.Recipient, self.Value, self.TransactionHash, 2, inputData['CoinHash']))
               
               #add the transactions to the main chain UTXO list
               for i in self.TransactionOutputs:
                    MainChain.UTXOs[i.Id] = {'Transaction':i}
               
               #remove spent transactions
               for i in self.TransactionInputs:
                    if i.UTXO is None:
                         continue

                    MainChain.UTXOs.pop(i.TransactionOutputId, None)
               
               return True
          
          #this transaction type burns a value of a token held by owner
          if self.TransactionType == 3:
               
               
               #Checks to prevent bad things from happening
               inputData = self.MiscData
               try:
                    if inputData == None:
                         print("No Arguments Given")
                         return False
                    
                    if type(inputData) != type(dict()):
                         print("Coin parameters not given in correct type")
                         return False
                         
                    if type(inputData['CoinHash']) != type("") or len(inputData['CoinHash']) < 1:
                         print("Coin Hash not given correctly")
                         return False
                    
                    if inputData['CoinHash'] not in MainChain.AlternativeCoins:
                         print("Coin not found")
                         return False
               except Exception as e:
                    print("Error processing coin creation data: " + e)
                    return False
               
               
               #check all UTXOs on the chain
               for i in range(len(self.TransactionInputs)):
                    #if MainChain.UTXOs[self.TransactionInputs[i]]['Transaction'].TransactionType == 2 and MainChain.UTXOs[self.TransactionInputs[i]]['Transaction'].Data == inputData['CoinHash']:
                         
                    inp = ins.TransactionInput(self.TransactionInputs[i])
                    inp.UTXO = MainChain.UTXOs[self.TransactionInputs[i]]['Transaction']
                    self.TransactionInputs[i] = inp
                    
               
               if self.GetInputsValue() < self.Value:
                    print("Trying to send token value more than amount owned")
                    return False
               
               #calculate the order hash and the total left from the input transactions
               _LeftOverValue = self.GetInputsValue() - self.Value
               self.TransactionHash = self.CalculateHash()
               
               #create the transaction outputs and add them to the output list
               self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, _LeftOverValue, self.TransactionHash, 2, inputData['CoinHash']))
               
               #add the transactions to the main chain UTXO list
               for i in self.TransactionOutputs:
                    MainChain.UTXOs[i.Id] = {'Transaction':i}
               
               #remove spent transactions
               for i in self.TransactionInputs:
                    if i.UTXO is None:
                         continue

                    MainChain.UTXOs.pop(i.TransactionOutputId, None)
               
               return True
          
          #this transaction type freezes a set of tokens held by an owner
          if self.TransactionType == 4:
               
               
               #Checks to prevent bad things from happening
               inputData = self.MiscData
               try:
                    if inputData == None:
                         print("No Arguments Given")
                         return False
                    
                    if type(inputData) != type(dict()):
                         print("Coin parameters not given in correct type")
                         return False
                         
                    if type(inputData['CoinHash']) != type("") or len(inputData['CoinHash']) < 1:
                         print("Coin Hash not given correctly")
                         return False
                    
                    if inputData['CoinHash'] not in MainChain.AlternativeCoins:
                         print("Coin not found")
                         return False
                    
                    if type(inputData['Freeze']) != type(False):
                         print("Freeze State Incorrect type")
                         return False
                    
               except Exception as e:
                    print("Error processing coin creation data: " + e)
                    return False
               
               #check all UTXOs on the chain
               for i in range(len(self.TransactionInputs)):
                    #if MainChain.UTXOs[self.TransactionInputs[i]]['Transaction'].TransactionType == 2 and MainChain.UTXOs[self.TransactionInputs[i]]['Transaction'].Data == inputData['CoinHash']:
                         
                    inp = ins.TransactionInput(self.TransactionInputs[i])
                    inp.UTXO = MainChain.UTXOs[self.TransactionInputs[i]]['Transaction']
                    self.TransactionInputs[i] = inp
                    
               if self.GetInputsValue() < self.Value:
                    print("Trying to freeze token value more than amount owned")
                    return False
               
               #calculate the order hash and the total left from the input transactions
               _LeftOverValue = self.GetInputsValue() - self.Value
               self.TransactionHash = self.CalculateHash()
               
               if inputData['Freeze'] == True:
                    #create the transaction outputs and add them to the output list
                    self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, _LeftOverValue, self.TransactionHash, 2, inputData['CoinHash']))
                    frozenOut =outs.TransactionOutput(self.Sender, self.Value, self.TransactionHash, 2, inputData['CoinHash'])
                    frozenOut.Frozen =  True
                    self.TransactionOutputs.append(frozenOut)
               else:
                    #create the transaction outputs and add them to the output list
                    fr = outs.TransactionOutput(self.Sender, _LeftOverValue, self.TransactionHash, 2, inputData['CoinHash'])
                    fr.Frozen = True
                    self.TransactionOutputs.append(fr)
                    self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, self.Value, self.TransactionHash, 2, inputData['CoinHash']))
                    
               #add the transactions to the main chain UTXO list
               for i in self.TransactionOutputs:
                    MainChain.UTXOs[i.Id] = {'Transaction':i}
               
               #remove spent transactions
               for i in self.TransactionInputs:
                    if i.UTXO is None:
                         continue

                    MainChain.UTXOs.pop(i.TransactionOutputId, None)
               
               return True
          
          #this transaction type creates a limit order
          if self.TransactionType == 5:
               
               #Checks to prevent bad things from happening
               inputData = self.MiscData
               try:
                    if inputData == None:
                         print("No Arguments Given")
                         return False
                    
                    if type(inputData) != type(dict()):
                         print("Coin parameters not given in correct type")
                         return False
                         
                    if type(inputData['CoinHash']) != type("") or len(inputData['CoinHash']) < 1:
                         print("Coin Hash not given correctly")
                         return False
                    
                    if inputData['CoinHash'] not in MainChain.AlternativeCoins:
                         print("Coin not found")
                         return False
                    
                    if type(inputData['Rate']) != type(1) and type(inputData['Rate']) != type(0.1) :
                         print("Rate is incorrect type")
                         return False
                    
                    if inputData['Rate'] <= 0:
                         print("Rate is impossibly small")
                         return False
                    
                    if type(inputData['BuyFlag']) != type(True):
                         print("Flag is not a boolean type")
                         return False
                    
                    if type(inputData['Total']) != type(1):
                         print("Total is incorrect type")
                         return False
                    
                    if inputData['Total'] <= 0:
                         print("Total is impossibly small")
                         return False
                    
               except Exception as e:
                    print("Error processing limit order: " + e)
                    return False
               
               #check for any matching order instances
               if len(MainChain.OpenOrders) <= 0:
                    
                    #this is our genesis transaction for the new coin!
                    output = outs.TransactionOutput(self.Sender, 1, self.TransactionHash, 5, inputData)
                    self.TransactionOutputs.append(output)
                    
                    data = {"market":inputData['CoinHash'],"TransactionID":output.Id, "inputs":self.TransactionInputs,"InputData":inputData, "sender":self.Sender}
                    MainChain.OpenOrders.append(data)
                    return True
               
               # look for a suitable trade
               else:
                    for i in MainChain.OpenOrders:
                         
                         #this is a rare type, this is when a trade can actually happen because equilibria in the market
                         if i['market'] == inputData['CoinHash'] and i['InputData']['BuyFlag'] != inputData['BuyFlag'] and i['InputData']["Rate"] == inputData['Rate']:
                              
                              
                              #check all UTXOs for the new order
                              for j in range(len(self.TransactionInputs)):
                                   
                                   inp = ins.TransactionInput(self.TransactionInputs[j])
                                   inp.UTXO = MainChain.UTXOs[self.TransactionInputs[j]]['Transaction']
                                   self.TransactionInputs[j] = inp
                              
                              #check all UTXOs for the existing  order
                              for j in range(len(i['inputs'])):
                                   inp = ins.TransactionInput(i['inputs'][j])
                                   inp.UTXO = MainChain.UTXOs[i['inputs'][j]]['Transaction']
                                   i['inputs'][j] = inp
                                   
                              
                              totalTrade = 0
                              #calculate the total trade value
                              if i['InputData']["Total"] == inputData['Total']:
                                   totalTrade = inputData['Total']
                              elif i['InputData']["Total"] < inputData['Total']:
                                   totalTrade = i['InputData']["Total"]
                              elif i['InputData']["Total"] > inputData['Total']:
                                   totalTrade = inputData['Total']
                              
                              Value = totalTrade * inputData['Rate']
                              
                              if i['InputData']['BuyFlag'] == True:
                                   
                                   #calculate the order hash and the total left from the input transactions
                                   NativeTradeLeftover = self.GetInputsValueList(i['inputs']) - Value
                                   self.TransactionHash = self.CalculateHash()
                              
                                   #create the transaction outputs and add them to the output list
                                   self.TransactionOutputs.append(outs.TransactionOutput(i['sender'], NativeTradeLeftover, self.TransactionHash, 0))
                                   self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, Value, self.TransactionHash, 0))
                                   
                                   #calculate the order hash and the total left from the input transactions
                                   _LeftOverValue = self.GetInputsValue() - totalTrade
                                   self.TransactionHash = self.CalculateHash()
                                   
                                   #create the transaction outputs and add them to the output list
                                   self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, _LeftOverValue, self.TransactionHash, 2, inputData['CoinHash']))
                                   self.TransactionOutputs.append(outs.TransactionOutput(i['sender'], totalTrade, self.TransactionHash, 2, inputData['CoinHash']))
                                   
                              
                                   #add the transactions to the main chain UTXO list
                                   for j in self.TransactionOutputs:
                                        MainChain.UTXOs[j.Id] = {'Transaction':j}
                                   
                                   #remove spent transactions
                                   for j in self.TransactionInputs:
                                        if j.UTXO is None:
                                             continue
                    
                                        MainChain.UTXOs.pop(j.TransactionOutputId, None)
                                   
                                   
                                   if i['InputData']["Total"] - totalTrade == 0:
                                        print(i)
                                   return True
                              
                              else:
                                   
                                   #calculate the order hash and the total left from the input transactions
                                   NativeTradeLeftover = self.GetInputsValueList() - Value
                                   self.TransactionHash = self.CalculateHash()
                              
                                   #create the transaction outputs and add them to the output list
                                   self.TransactionOutputs.append(outs.TransactionOutput(i['sender'], Value, self.TransactionHash, 0))
                                   self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, NativeTradeLeftover, self.TransactionHash, 0))
                                   
                                   #calculate the order hash and the total left from the input transactions
                                   _LeftOverValue = self.GetInputsValue() - totalTrade
                                   self.TransactionHash = self.CalculateHash()
                                   
                                   #create the transaction outputs and add them to the output list
                                   self.TransactionOutputs.append(outs.TransactionOutput(self.Sender, totalTrade, self.TransactionHash, 2, inputData['CoinHash']))
                                   self.TransactionOutputs.append(outs.TransactionOutput(i['sender'], _LeftOverValue, self.TransactionHash, 2, inputData['CoinHash']))
                                   
                              
                                   #add the transactions to the main chain UTXO list
                                   for j in self.TransactionOutputs:
                                        MainChain.UTXOs[j.Id] = {'Transaction':j}
                                   
                                   #remove spent transactions
                                   for j in self.TransactionInputs:
                                        if j.UTXO is None:
                                             continue
                    
                                        MainChain.UTXOs.pop(j.TransactionOutputId, None)
                                        

                                   #c = i['InputData']
                                   #c["Total"] = c["Total"] - totalTrade  
                                   #i['InputData']["Total"] = i['InputData']["Total"] - totalTrade      
                                   return True
                              
                         else:
                              #this is our genesis transaction for the new coin!
                              output = outs.TransactionOutput(self.Sender, 1, self.TransactionHash, 5, inputData)
                              self.TransactionOutputs.append(output)
                              
                              data = {"market":inputData['CoinHash'],"TransactionID":output.Id, "InputData":inputData, "sender":self.Sender}
                              MainChain.OpenOrders.append(data)
                              return True
                              
                    
                    
                    
               
               
               
     def GetInputsValue(self):
          
          _total = 0
          
          for i in self.TransactionInputs:
               if i.UTXO is None:
                    continue
               _total += i.UTXO.Value
               
          
          return _total
     
     def GetInputsValueList(self, inputs):
          _total = 0
          
          for i in inputs:
               if i.UTXO is None:
                    continue
               _total += i.UTXO.Value
               
          return _total
     
     def GetOutputsValue(self):
          
          _total = 0

          for i in self.TransactionOutputs:

               _total += i.Value
               

          return _total
          
          
          
          
          
          
          
          
          
          
          
          
          