# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 18:46:37 2018

@author: Khera

this class simulates the consensus/blockchain - this is because my networking is really bad so the Client.py file does not work as expected.
this class is essentially what Client.py was meant to become
"""

import LocalClient as node
import Block as bl
import Transaction as txn
import TransactionInput as ins
import TransactionOutput as outs
import Wallet as wlt
import UtilFunctions as utils
import random
from threading import Thread
import time
class Simulator():
     
     OfficialBlockchain = []
     AlternativeCoins = []
     OpenOrders = []
     Markets = []
     difficulty = 1 # remove this eventually...
     MinimumTransactionValue = 0.0000001
     UTXOs = dict()
     TransactionQueue = []
     CandidateBlocks = []
     
     
     def __init__(self):
          self.nodes = []
          self.KnowAddresses = []
          self.Blockchain = []
          self.AlternativeCoins = []
          self.OpenOrders = []
          self.UTXOs = dict()
          self.Markets = []
          self.Coinbase = ""
          self.ElectedNode = 0
          self.State = 0
          self.TransactionQueue = []
          self.CandidateBlocks = []
          self.ConstructorNode = 0
          self.ValidatorNodes = []
          self.GenesisTransaction = 0
          self.LastBlock = ""
          
          ##
          self.InitNodes(5)
          self.Genesis()
          self.DistributeFunds()
          #self.PrintBalances()
          self.ConsensusThread = Thread(target = self.Consensus)
          self.ConsensusThread.start()
          
     
     
     #initialise a set of nodes
     #store the addresses in a list
     def InitNodes(self, numNodes):
          
          for i in range(numNodes):
               NewNode = node.LocalClient(self)
               self.nodes.append(NewNode)
               self.KnowAddresses.append(NewNode.MainWallet.PEMPublicKey)
     
     #generate the initial Genesis Transaction/Block
     def Genesis(self):
          
          #generate some walets
          Coinbase1 = wlt.Wallet()
          self.Coinbase = wlt.Wallet()
          
          #send 10000 coins to coinbase
          genesisTransaction = txn.Transaction(Coinbase1.PEMPublicKey.decode(), self.Coinbase.PEMPublicKey.decode(), 100000, 0, None)
          genesisTransaction.GenerateTransactionSignature(Coinbase1.PrivateKey)
          self.GenesisTransaction = genesisTransaction
          
          #give the transaction a manual hash
          genesisTransaction.TransactionHash = "0"
          genesisTransaction.TransactionOutputs.append(outs.TransactionOutput(genesisTransaction.Recipient, genesisTransaction.Value, genesisTransaction.TransactionHash,0))
          self.UTXOs[genesisTransaction.TransactionOutputs[0].Id] = {"Transaction":genesisTransaction.TransactionOutputs[0]}
          
          print("create and mine genesis block")
          genesis = bl.Block("0")
          genesis.AddTransaction(genesisTransaction, self)
          self.AddBlock(genesis)
     
     #give spending money to the blocks
     def DistributeFunds(self):
          block1 = bl.Block(self.Blockchain[len(self.Blockchain)-1].BlockHash)
          for i in self.KnowAddresses:
               block1.AddTransaction(self.Coinbase.SendFunds(i, 1000, self), self)
          
          self.AddBlock(block1)
          self.LastBlock = block1
          
     def AddBlock(self, NewBlock):
          NewBlock.MineBlock(0)
          self.Blockchain.append(NewBlock)
     
     def PrintBalances(self):
          for i in self.KnowAddresses:
               print(self.GetAddressBalance(i))
               
     def GetBalances(self):
          balances = []
          for i in self.KnowAddresses:
               balances.append(self.GetAddressBalance(i))
          return balances
               
     #get the balance of all of the know wallets
     def GetAddressBalance(self, address):
          total = 0
          for i in self.UTXOs:
               
               if self.UTXOs[i]['Transaction'].Recipient == address and self.UTXOs[i]['Transaction'].TransactionType == 0:
                    total+= self.UTXOs[i]['Transaction'].Value
          
          return total
     
     
     #hold a simple election to select the next node
     def HoldElection(self):
          
          lower = 0
          bounds = []
          balances = self.GetBalances()
          
          total = 0
          for i in balances:
               total += i
          
          for i in balances:
               lower += i
               bounds.append(lower/total)
          
          r = random.uniform(0,1)
          
          elected = 0
          
          for i in range(len(bounds)):
               
               if i == 0 and r < bounds[i]:
                    elected = i
               elif r<bounds[i] and r > bounds[i-1]:
                    elected = i
          
          self.ElectedNode = elected
     
     #this thread deals with Elections, Block Validation and Block Creation
     def Consensus(self):
          
          while True:

               if self.State == 0:
#                    transactionSim = Thread(target = self.SimulateFundSendTransactions)
#                    transactionSim.start()
                    
                    self.ConstructorNode = 0
                    self.ValidatorNodes = []
                    self.CandidateBlocks = []
                    
                    #elect a node
                    self.HoldElection()
                    
                    for i in range(len(self.nodes)):
                         #this resets the nodes states, so they are inline with the states of "Master/Block Producer"
                         #This is not eally neaded and it is VERY INTENSIVE
                         self.nodes[i].ResetToNetworkLevel()
                    
                    for i in range(len(self.nodes)):

                         if self.ElectedNode == i:
                              print("Elected")
                              self.ConstructorNode = self.nodes[i]
                              #self.ConstructorNode = self
                              
                         else:
                              
                              self.ValidatorNodes.append(self.nodes[i])
                    
                    self.State = 1
               
               #spend 5 seconds creating a block
               elif self.State == 1:
                    
                    self.ConstructorNode.CreateBlock()
                    self.CandidateBlocks.append(self.ConstructorNode.Blockchain[len(self.ConstructorNode.Blockchain)-1])
                    self.State = 2
               
               #get the validators to validate the chain
               elif self.State == 2:
                    try:
                         validations = []
                         count = 0
                         for i in self.ValidatorNodes:
                                   
                                   i.AddBlock(self.CandidateBlocks[0])
                                   validations.append(i.CheckChainValid(self.GenesisTransaction))
                         
                         for i in validations:
                              if i == True:
                                   count += 1
                    except Exception as e:
                         print(e)
                         
                         
                    #if half the nodes are saying yes, then add it to the block chain
                    try:
                         if count/len(validations) >=0.5:
                              #self.CandidateBlocks[0].ProcessTransactions(self)
                              self.AddBlock(self.CandidateBlocks[0])
                              self.CheckChainValid()
                              #self.LastBlockHash = self.CandidateBlocks[0].BlockHash
                              for i in self.CandidateBlocks[i].transactions:
                                   if i in self.TransactionQueue:
                                        self.TransactionQueue.remove(i)
                    except Exception as e:
                         print(e)
                         
                    self.State = 0
     
     #add the transaction to the 
     def AddTransactionToQueue(self, Txn):
          self.TransactionQueue.append(Txn)
     
     #simulate some transactions
     def SimulateFundSendTransactions(self):
          while(True):
               time.sleep(0.5)
               r = int(random.randrange(0, len(self.nodes)-1))
               r1 = r
               
               while r == r1:
                    r1 = int(random.randrange(0, len(self.nodes)-1))
               
               
               value = random.uniform(0.5, 15)
               
               newTx = self.nodes[r].MainWallet.SendFunds(self.nodes[r1].MainWallet.PEMPublicKey.decode(), value, self)
               self.AddTransactionToQueue(newTx)
               
          #Create a Block
     def CreateBlock(self):
          print(self.Blockchain[len(self.Blockchain)-1].BlockHash)
          newBlock = bl.Block(self.Blockchain[len(self.Blockchain)-1].BlockHash)
          newBlock.validator = self.Coinbase.PEMPublicKey # might not need this?
          
          timeout = time.time() + 5
          while time.time() <= timeout:
               for i in self.TransactionQueue:
                    
                    if i not in newBlock.transactions:
                         newBlock.AddTransaction(i, self)
          
          self.AddBlock(newBlock)
          self.CandidateBlocks.append(newBlock)
          
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
                    print(currentBlock.PreviousHash)
                    print(previousBlock.BlockHash)
                    #time.sleep(1)
                    #print(i)
                    
                    return False
               
               
               for j in currentBlock.transactions:
                    
                    currentTransaction = j
                    
                    if currentTransaction.TransactionType == 0:
                    
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
          self.UTXOs = tempUTXO
          return True
          
       #%%   

Simulator()



















