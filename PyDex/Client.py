# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 09:53:49 2018

@author: Khera

Client combines the Node/Networking side of things, with the Consensus AND Wallet Elements
"""

import Block as bl
import Transaction as txn
import TransactionInput as ins
import TransactionOutput as outs
import Wallet as wlt
import Node as node

import UtilFunctions as utils
import zmq

from threading import Thread
import time
import argparse
from json import JSONEncoder
import json

class Client():
     
     
     wallets = []
     mainWallet = ""
     node = ""
     
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
     
     def __init__(self):
          self.wallets = []
          self.mainWallet = wlt.Wallet()
          self.wallets.append(self.mainWallet)
          self.node = node.Node()
          
          self.Blockchain = []
          self.UTXOs = dict()
          self.MinimumTransactionValue = 0.000000000001
          self.ConstructMode = False
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
          
     #clears spent transactions
     def CleanUpUtxo(self):
          
          newUTXO = dict()
          
          for i in self.UTXOs:
               
               if self.UTXOs[i]['Transaction'].Spent == False:
                    newUTXO[i] = {'Transaction':self.UTXOs[i]['Transaction']}
          
          self.UTXOs = newUTXO
     
     def WaitForTransactions(self):
          while True:
               
               if len(self.node.obs) > 0:
                    for i in self.node.obs:
                         if type(i) == "transaction.transaction":
                              
                              self.TransactionQue.append(i)
                              self.node.obs.remove(i)
                         
                         elif type(i) == "block.block":
                              
                              self.CandidateBlocks.append(i)
                              self.node.obs.remove(i)
     
     
     #creating a new block, that once a thread has ended, will then return a block
     def ConstructBlock(self):
          
          timer = Thread(target = self.ConstructMode)
          timer.start()
          
          newBlock = bl.Block(self.Blockchain[len(self.Blockchain)-1].BlockHash)
          addedTransactions = []
          while self.ConstructBlock == True:
               
               if len(self.TransactionQue > 0):
                    for i in self.TransactionQue:
                         
                         if i not in addedTransactions:
                              
                              newBlock.AddTransaction(i)
                              addedTransactions.append(i)
          
          for i in addedTransactions:
               self.TransactionQue.remove(i)
          
          return newBlock
     
     #method takes a block and sends it via the clients node
     def BroadCastBlock(self, newBlock):
          
          self.node.SendDataMasterNode(newBlock)
     
     #creates a node and broadcasts
     def CreateBlockAndBroadCast(self):
          newBlock = self.ConstructBlock()
          self.BroadCastBlock(newBlock)
     
     #creates a transaction from the main wallet and sends it to the nodes
     def BroadCastTransaction(self, _recipient, _value):
          
          tx = self.mainWallet.SendFunds(_recipient, _value, self)
          self.node.SendDataMasterNode(tx)
     
     #timer thread used to time the construction of a block
     def ConstructMode(self):
          
          time.sleep(15)
          #basically building a block until block time is over. consensus signals node and backup node to do the building
          self.ConstructBlock = False
     
     #start the threads like listening for new transactions and blocks.
     def StartAllThreads(self):
          
          NodeService = Thread(target = self.WaitForTransactions)
          NodeService.start()
     
Heph = Client()
Heph.initCoin()

          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          