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
     Data = ""
     TimeStamp = ""
     nonce = 0
     
     def calculateHash(self):
          hashingData = str(self.Data)+ "_" +str(self.TimeStamp) + "_" + str(self.PreviousHash)
          return utils.UtilFunctions.applySha256(utils.UtilFunctions, hashingData)
     
     #class constructor
     #block has prev hash, current hash, timestamp and data
     def __init__(self, _data, _previousHash):
          
          self.Data = _data
          self.PreviousHash = _previousHash
          self.TimeStamp = time.time()
          self.BlockHash = self.calculateHash()
          self.nonce = 0
     
     
     #PoW approach for now, mine block is standard PoW type stuff
     def MineBlock(self, difficulty):
          
          while(self.nonce != difficulty):
               
               self.nonce = self.nonce+1
               self.BlockHash = self.calculateHash()
          
          print("block mined: " + self.BlockHash)
               