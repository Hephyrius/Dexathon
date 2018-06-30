# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 02:47:27 2018

@author: Harnick Khera github/hephyrius

main class for running and operating the blockchain

"""

import Block as bl
import Transaction as txn
import TransactionInput as ins
import TransactionOutput as outs
import Wallet as wlt

import UtilFunctions as utils
import zmq

from threading import Thread
import time

from json import JSONEncoder
import json

#helper function used for dumping the blockchain to a file
class myencoder(JSONEncoder):
     
     def default(self, o):
            return o.BlockHash, o.Data, o.PreviousHash, o.TimeStamp
     

class HephDex:
     
     Blockchain = []
     
     #temporarily a PoW approach while creating fundamentals. PoS is more complex!
     difficulty = 0 # TODO: Remove this
     
     #minimum spend for native coin
     MinimumTransactionValue = 0.000000000001
     
     #all unspent transactions on the blockchain
     UTXOs = dict()
     
     #keep a "map" of all the validators on the network
     Validators = dict()
     
     #storing blocks temporarily -- used in DPOS
     TemporaryBlocks = []
     CandidateBlocks = []
     TransactionQue = []
     #announcement is sent to all nodes
     Announcement = ""
     
     #init the blockchain
     def __init__(self):
          self.Blockchain = []
          self.UTXOs = dict()
          self.MinimumTransactionValue = 0.000000000001
          self.Validators = dict()
          self.CandidateBlocks = []
          self.TemporaryBlocks = []
          self.TransactionQue = []
          self.Announcement = ""
     
     def AddBlock(self, NewBlock):
          NewBlock.MineBlock(0)
          self.Blockchain.append(NewBlock)
     
     #verify the blockchain integrity
     def CheckChainValid(self, genesisTransaction):
          #check that the chain is solid
          tempUTXO = dict()
          tempUTXO[genesisTransaction.TransactionOutputs[0].Id] = {"Transaction":genesisTransaction.TransactionOutputs[0]}
          
          for i in range(1,len(self.Blockchain)):
               
               currentBlock = self.Blockchain[i]
               previousBlock = self.Blockchain[i-1]
               
               if currentBlock.BlockHash != currentBlock.calculateHash():
                    print("Different current and calculated hashes")
                    return False
               
               if currentBlock.PreviousHash != previousBlock.BlockHash:
                    print("Previous and Current hashes are different")
                    return False
               
               
               for j in currentBlock.transactions:
                    
                    currentTransaction = j
                    
                    if currentTransaction.GetInputsValue() != currentTransaction.GetOutputsValue():
                         print("Inputs are not equal to outputs")
                         return False
                    
                    
                    if currentTransaction.VerifyTransactionSignature() == False:
                         
                         print("Unable to verify Transaction")
                         return False
                    
                    for k in currentTransaction.TransactionInputs:
                         
                         tempOutput = tempUTXO[k.TransactionOutputId]
                         
                         if tempOutput == None:
                              print("Input Transaction Missing")
                         
                         if(k.UTXO.Value != tempOutput['Transaction'].Value):
                              print("Referenced input used in transaction is not valud")
                         
                         tempUTXO.pop(k.TransactionOutputId)
                    
                    for k in currentTransaction.TransactionOutputs:
                         
                         tempUTXO[k.Id] = {"Transaction":k}
                    
                    hasRecipient = False
                    hasSender = False
                    
                    for k in currentTransaction.TransactionOutputs:
                         
                         if k.Recipient == currentTransaction.Recipient:
                              hasRecipient = True
                              
                         if k.Recipient == currentTransaction.Sender:
                              hasSender = True
                    
                    if hasSender == False:
                         
                         print("Output residual do not reference the sender")
                         return False
                    
                    if hasRecipient == False:
                         
                         print("Output sent does not reference the reciever")
                         return False
               
          print("Blockchain is Valid")     
          return True
     
     #used to simulate a chain
     def initCoin(self):
          
          #generate some walets
          Coinbase = wlt.Wallet()
          walletA = wlt.Wallet()
          
          #send 100 coins to walleta
          genesisTransaction = txn.Transaction(Coinbase.PublicKey, walletA.PublicKey, 100, 0, None)
          genesisTransaction.GenerateTransactionSignature(Coinbase.PrivateKey)
          
          #give the transaction a manual hash
          genesisTransaction.TransactionHash = "0"
          genesisTransaction.TransactionOutputs.append(outs.TransactionOutput(genesisTransaction.Recipient, genesisTransaction.Value, genesisTransaction.TransactionHash))
          self.UTXOs[genesisTransaction.TransactionOutputs[0].Id] = {"Transaction":genesisTransaction.TransactionOutputs[0]}
          
          print("create and mine genesis block")
          genesis = bl.Block("0")
          genesis.AddTransaction(genesisTransaction, self)
          self.AddBlock(genesis)
          
          
     def StartNetworkThread(self):
          context = zmq.Context()
          socket = context.socket(zmq.REP)
          socket.bind("tcp://*:5555")
          while True:
              #  Wait for next request from client
              message = socket.recv()
              print("Received request: %s" % message)
          
              #  Do some 'work'
              time.sleep(1)
          
              #  Send reply back to client
              socket.send(b"World")
          
          
     #clears spent transactions
     def CleanUpUtxo(self):
          
          newUTXO = dict()
          
          for i in self.UTXOs:
               
               if self.UTXOs[i]['Transaction'].Spent == False:
                    newUTXO[i] = {'Transaction':self.UTXOs[i]['Transaction']}
          
          self.UTXOs = newUTXO
     
     
          
          
     
Heph = HephDex()
Heph.initCoin()
#thread = Thread(target = Heph.StartNetworkThread)
#thread.setDaemon(True)
#thread.start()


