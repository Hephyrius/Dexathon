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
import pickle

class Client():
     
     wallets = []
     mainWallet = ""
     node = ""
     Blockchain = []
     AlternativeCoins = []
     OpenOrders = []
     Markets = []
     #temporarily a PoW approach while creating fundamentals. PoS is more complex!
     difficulty = 0 #Remove this?
     
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
     AcceptedBlocks = []
     
     #announcement is sent to all nodes
     Announcement = ""
     
     #nodestate - what is this node currently doing - state machine
     State = 0
     
     #State machine for the client
     InputState = 0
     
     def __init__(self):
          self.wallets = []
          self.mainWallet = wlt.Wallet()
          self.wallets.append(self.mainWallet)
          self.node = node.Node()
          self.AcceptedBlocks = []
          self.Blockchain = []
          self.UTXOs = dict()
          self.MinimumTransactionValue = 0.000000000001
          self.ConstructMode = False
          self.Validators = dict()
          self.CandidateBlocks = []
          self.TemporaryBlocks = []
          self.TransactionQue = []
          self.Announcement = ""
          self.Genesis = ""
          self.State = 0
          self.AlternativeCoins = []
          self.OpenOrders = []
          self.Markets = []
          self.InputState = 0
          #start the blockchain
          self.StartClient()
          
     def AddBlock(self, NewBlock):
          NewBlock.MineBlock(0)
          self.Blockchain.append(NewBlock)
          
     def CleanOrders(self):
          newOrder = []
          for i in self.OpenOrders:
               if i['InputData']['Total'] > 0:
                    newOrder.append(i)
                    
          self.OpenOrders = newOrder
          
     #verify the blockchain integrity
     def CheckChainValid(self):
          genesisTransaction = self.Blockchain[0].transactions[0]
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
     
     #verify the blockchain integrity
     def CheckNewChainValid(self, genesisTransaction, _NewBlockchain):
          #check that the chain is solid
          tempUTXO = dict()
          tempUTXO[genesisTransaction.TransactionOutputs[0].Id] = {"Transaction":genesisTransaction.TransactionOutputs[0]}
          
          for i in range(1,len(_NewBlockchain)):
               
               currentBlock = _NewBlockchain[i]
               previousBlock = _NewBlockchain[i-1]
               
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
          
          #send 100 coins to walleta
          genesisTransaction = txn.Transaction(Coinbase.PEMPublicKey.decode(), self.mainWallet.PEMPublicKey.decode(), 10000000000, 0, None)
          genesisTransaction.GenerateTransactionSignature(Coinbase.PrivateKey)
          
          #give the transaction a manual hash
          genesisTransaction.TransactionHash = "0"
          genesisTransaction.TransactionOutputs.append(outs.TransactionOutput(genesisTransaction.Recipient, genesisTransaction.Value, genesisTransaction.TransactionHash, 0))
          self.UTXOs[genesisTransaction.TransactionOutputs[0].Id] = {"Transaction":genesisTransaction.TransactionOutputs[0]}
          self.Genesis = genesisTransaction
          
          print("create and mine genesis block")
          genesis = bl.Block("0")
          genesis.AddTransaction(genesisTransaction, self)
          self.AddBlock(genesis)
          self.AcceptedBlocks.append(genesis)
          self.node.AcceptedBlockData = self.AcceptedBlocks
          self.SendGenesisData(Coinbase, self.mainWallet)
          
          
     #clears spent transactions
     def CleanUpUtxo(self):
          
          newUTXO = dict()
          
          for i in self.UTXOs:
               
               if self.UTXOs[i]['Transaction'].Frozen == False:
                    newUTXO[i] = {'Transaction':self.UTXOs[i]['Transaction']}
          
          self.UTXOs = newUTXO
     
     def WaitForData(self):
          while True:
               
               if len(self.node.obs) > 0:
                    for i in self.node.obs:
                         if type(i) == type(txn.Transaction(0,0,0,0,0)):
                              
                              self.TransactionQue.append(i)
                              self.node.obs.remove(i)
                         
                         elif type(i) == type(bl.Block(0)):
                              
                              self.CandidateBlocks.append(i)
                              self.node.obs.remove(i)
                         elif type(i) == type([]):

                              if type(i[0]) == type(bl.Block(0)):
                                   self.AcceptedBlocks = i
                                   self.node.obs.remove(i)

     
     
     #creating a new block, that once a thread has ended, will then return a block
     def ConstructBlock(self):
#          
#          timer = Thread(target = self.ConstructMode)
#          timer.start()
          
          newBlock = bl.Block(self.Blockchain[len(self.Blockchain)-1].BlockHash)
          newBlock.validator = self.mainWallet.PEMPublicKey # might not need this?
          addedTransactions = []
          timeout = time.time() + 10
          
          while time.time()<=timeout:
               
               if len(self.TransactionQue)>0:
                    for i in self.TransactionQue:
                         
                         if i not in addedTransactions:
                              
                              newBlock.AddTransaction(i, self)
                              addedTransactions.append(i)
          
          if len(addedTransactions)>0:
               for i in addedTransactions:
                    self.TransactionQue.remove(i)
          
          return newBlock
     
     def SendAllBlocks(self):
          for i in self.Blockchain:
               p = pickle.dumps(i)
               self.node.SendDataToAll(p)
     
     #method takes a block and sends it via the clients node
     def BroadCastBlock(self, newBlock):
          self.node.SendDataMasterNode(newBlock)
     
     #creates a node and broadcasts
     def CreateBlockAndBroadCast(self):
          newBlock = self.ConstructBlock()
          newBlock.MineBlock(0)
          self.AcceptedBlocks.append(newBlock)
          self.node.AcceptedBlockData = self.AcceptedBlocks
          self.AddBlock(newBlock)
          p = pickle.dumps(newBlock)
          self.node.SendDataToAll(p)
     
     #creates a transaction from the main wallet and sends it to the nodes
     def BroadCastTransaction(self, tx):
          
          self.TransactionQue.append(tx)
          p = pickle.dumps(tx)
          self.node.SendDataToAll(p)
     
     #timer thread used to time the construction of a block
     def ConstructMode(self):
          
          time.sleep(15)
          #basically building a block until block time is over. consensus signals node and backup node to do the building
          self.ConstructBlock = False
     
     #start the threads like listening for new transactions and blocks.
     def StartAllThreads(self):
          
          NodeService = Thread(target = self.WaitForTransactions)
          NodeService.start()
     
     #declare a stake on the node network - no repercussions for this YET
     def RegisterStake(self,_StakeValue):
          if(_StakeValue < self.mainWallet.getBalance(self)):          
               self.node.RegisterStake(self.mainWallet.PublicKey, self.node.ThisSocket, _StakeValue)
               print("Successfully Staking Tokens")
     
     #remove a stake from the node networks
     def RemoveStake(self):
          if self.node.ThisSocket in self.node.DiscoveredNodes:
               del self.node.DiscoveredNodes[self.node.ThisSocket]
     
     #package the genesisdata and send it to all clients
     def SendGenesisData(self, coinbase, walletA):
          time.sleep(5)
          genesisData = self.Blockchain[0]
          p = pickle.dumps(genesisData)
          self.node.SendDataToAll(p)
     
     #add the genesis blockchain data to the client instance
     def AddGenesisData(self):
          while self.node.AcceptedBlockData == []:
               time.sleep(1)
               if self.node.GenesisData != []:
                    print("Found Genesis")
                    self.AcceptedBlocks = self.node.AcceptedBlockData
     
     def RestoreChainViaNode(self):
          self.node.SendRestore()
          time.sleep(4)
          self.AcceptedBlocks = self.node.AcceptedBlockData
          for i in self.AcceptedBlocks:
               #print(i)
               if type(i) == type(bl.Block(0)):
                    
                    self.AddBlock(i)
                    
     def ManuallyRestoreChain(self):
          for i in self.CandidateBlocks:
               if i not in self.Blockchain:
                    
                    self.AddBlock(i)
                    self.CandidateBlocks.remove(i)
               
     #validate a new block before updating local blockchain
     def ValidateBlock(self):
          tempChain = self.Blockchain
          if len(self.CandidateBlocks >0):
               for i in self.CandidateBlocks:
                    tempChain.append(i)
                    if self.CheckNewChainValid(self.Genesis, tempChain) == True and i not in self.Blockchain:
                         self.Blockchain.append(i)
                         self.CheckChainValid(self.Genesis)
                         break
                    
     # deal with basic commands. such as stake, send coin, make a new coin, place an order on the market ect
     # not implemented as such, wallet has these functions already, easier invoking them in code as its just a prototype!
     def ClientConsoleThread(self):
          history = []
          while True:
               if self.InputState == 0:
                    userinput = input("Console: ")
                    
                    if "send" in userinput:
                         self.InputState == 1
               
               if self.InputState == 1:
                    userinput = input("Token or Coin: ")
                    
                    if "token" in userinput:
                         history.append("token")

     
     def CheckBlockNotInChain(self, newBlock):
          BlkHash = newBlock.MineBlock(0)
          for i in self.Blockchain:
               if i.BlockHash == BlkHash:
                    return False
                    break
               
          return True
               
     #core client logic
     def StartClient(self):
          while True:
               print(self.State)
               #state one deals with Genesis and new nodes joining the chain
               if self.State == 0:
                    
                    if self.node.ThisSocket == 5555:
                         time.sleep(4)
                         self.initCoin()
                         self.DataThread = Thread(target = self.WaitForData)
                         self.DataThread.start()
                         
                         self.SimulatorThread = Thread(target = self.CreateArtificialTransactions)
                         self.SimulatorThread.start()
                    else:
                         self.DataThread = Thread(target = self.WaitForData)
                         self.DataThread.start()
                         self.RestoreChainViaNode()
                         self.ManuallyRestoreChain()
#                         self.node.SendDataToAll(self.mainWallet.PEMPublicKey)
                         print("Restored")
                         
                    self.State = 1
               
               #state one is election of node
               elif self.State == 1:
                    self.CandidateBlocks = []
                    self.node.HoldElections()
                    print(self.node.electedNode)
                    
                    if self.node.electedNode == self.node.ThisSocket or self.node.ThisSocket == 5555:
                         self.State = 2
                         
                    elif self.node.electedNode != self.node.ThisSocket:
                         self.State = 3
                         

               
               #produce blocks
               elif self.State == 2:
                    self.CreateBlockAndBroadCast()
                    self.CheckChainValid()
                    self.State = 1

                    
                    
               #act as a validator and wait for a new block
               elif self.State == 3:
                    if len(self.CandidateBlocks) > 0:
                         for i in self.CandidateBlocks:
                              if i not in self.Blockchain:
                                   self.CandidateBlocks.remove(i)
                                   self.AddBlock(i)
                                   self.CheckChainValid()
                                   self.State = 1
                              else:
                                   self.CandidateBlocks.remove(i)
                    else:
                         time.sleep(1)
     
     #function creates many transactions which can help simulate how the blockchain would behave under load - for a non-networked example look at Main.py!
     def CreateArtificialTransactions(self):
          
          wallet2 = wlt.Wallet()
#          tx = self.mainWallet.CreateNewCoin(self,"HephCoin", "Heph", 100000)
#          self.BroadCastTransaction(tx)
          
          while True:
               
               time.sleep(2)
               
               tx = self.mainWallet.SendFunds(wallet2.PEMPublicKey.decode(), 5, self)
               self.BroadCastTransaction(tx)
               
               
               

          
Heph = Client()
#%%
          
          
          
          
          