# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 02:49:32 2018

@author: Harnick Khera github/hephyrius

This class is responsible for blocks

"""

import time
import UtilFunctions as utils

class Block:
     
     BlockHash = ""
     PreviousHash = ""
     TimeStamp = ""
     nonce = 0
     merkelRoot = ""
     transactions = []
     validator = ""
     
     def calculateHash(self):
          hashingData =  str(self.TimeStamp) + "_" + str(self.PreviousHash) +str(self.merkelRoot) 
          return utils.UtilFunctions.applySha256(utils.UtilFunctions, hashingData)
     
     #class constructor
     #block has prev hash, current hash, timestamp and data
     def __init__(self, _previousHash, _validator=0):
          
          self.PreviousHash = _previousHash
          self.TimeStamp = time.time()
          self.BlockHash = self.calculateHash()
          self.nonce = 0
          self.transactions = []
          self.merkelRoot = ""
          self.validator = _validator
     
     
     #PoW approach for now, mine block is standard PoW type stuff
     def MineBlock(self, difficulty):
          self.merkelRoot = utils.UtilFunctions.GetMerkelRoot(self.transactions)
          self.nonce = self.nonce+1
          self.BlockHash = self.calculateHash()
          print("block hash is: " + self.BlockHash)
     
     #add transactions to block
     def AddTransaction(self, transaction, MainChain):
          
          if transaction == None:
               return False
          
          if self.PreviousHash != "0":
               if transaction.ProcessTransaction(MainChain) == False:
                    print("Transaction failed to be processed, discarded")
                    return False
          
          self.transactions.append(transaction)
          print("Transaction added to block")
          return True
     
     def ProcessTransactions(self, MainChain):
          for i in self.transactions:
               if i == None:
                    return False
               
               if self.PreviousHash != "0":
                    if i.ProcessTransaction(MainChain) == False:
                         print("Transaction failed to be processed, discarded")
                         return False
          
          