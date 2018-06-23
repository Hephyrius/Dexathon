# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 02:47:27 2018

@author: Khera

main class for running and operating the blockchain

"""

import Block as bl
import UtilFunctions
import json
from json import JSONEncoder

#helper function used for dumping the blockchain to a file
class myencoder(JSONEncoder):
     
     def default(self, o):
            return o.BlockHash, o.Data, o.PreviousHash, o.TimeStamp
     

class HephDex:
     
     Blockchain = []
     
     #temporarily a PoW approach while creating fundamentals. PoS is more complex!
     difficulty = 100000
     
     #init the blockchain
     def __init__(self):
          self.Blockchain = []
     
     #function used to verify block integrity
     def CheckChainValidity(self):
          
          currentBlock = 0
          previousBlock = 0
          
          for i in range(1,len(self.Blockchain)):
               currentBlock = self.Blockchain[i]
               previousBlock = self.Blockchain[i-1]
               
               if currentBlock.BlockHash != currentBlock.calculateHash():
                    print("Different current and calculated hashes")
                    return False
               
               if currentBlock.PreviousHash != previousBlock.BlockHash:
                    print("Previous and Current hashes are different")
                    return False
               
          return True
     
     #used for testing
     def main(self):
          
          #create some blocks
          self.Blockchain.append(bl.Block("GenesisBlock", "0x0"))
          self.Blockchain[len(self.Blockchain)-1].MineBlock(self.difficulty)
          
          self.Blockchain.append(bl.Block("SecondBlock", self.Blockchain[len(self.Blockchain)-1].BlockHash))
          self.Blockchain[len(self.Blockchain)-1].MineBlock(self.difficulty)
          
          self.Blockchain.append(bl.Block("ThirdBlock", self.Blockchain[len(self.Blockchain)-1].BlockHash))
          self.Blockchain[len(self.Blockchain)-1].MineBlock(self.difficulty)
          
          #dump to the file system
          dumpData = json.dumps(self.Blockchain, cls=myencoder)
     
          with open('chain.csv', 'w') as outfile:
               json.dump(dumpData, outfile)
          
          #check integrity
          if(self.CheckChainValidity() != True):
               print("error")
          else:
               print("Chain is valid")
     
Heph = HephDex()
Heph.main()