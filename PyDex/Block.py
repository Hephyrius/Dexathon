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
     
     def calculateHash(self):
          hashingData = str(self.Data)+ "_" +str(self.TimeStamp) + "_" + str(self.PreviousHash)
          print(hashingData)
          return utils.UtilFunctions.applySha256(utils.UtilFunctions, hashingData)
     
     #class constructor
     #block has prev hash, current hash, timestamp and data
     def __init__(self, _data, _previousHash):
          
          self.Data = _data
          self.PreviousHash = _previousHash
          self.TimeStamp = time.time()
          self.BlockHash = self.calculateHash()
          

          



#basic testing:

genesis = Block("first block", "0")
print(genesis.BlockHash)

second = Block("second block", genesis.BlockHash)
print(second.BlockHash)

third = Block("third block", second.BlockHash)
print(third.BlockHash)