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
import json
from json import JSONEncoder

#helper function used for dumping the blockchain to a file
class myencoder(JSONEncoder):
     
     def default(self, o):
            return o.BlockHash, o.Data, o.PreviousHash, o.TimeStamp
     

class HephDex:
     
     Blockchain = []
     AlternativeCoins = []
     OpenOrders = []
     Markets = []
     #temporarily a PoW approach while creating fundamentals. PoS is more complex!
     difficulty = 1
     MinimumTransactionValue = 0.001
     UTXOs = dict()
     #init the blockchain
     def __init__(self):
          self.Blockchain = []
          self.AlternativeCoins = []
          self.OpenOrders = []
          self.UTXOs = dict()
          self.Markets = []
     
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
     def HexCoin(self):
          
          #generate some walets
          Coinbase = wlt.Wallet()
          walletA = wlt.Wallet()
          walletB = wlt.Wallet()
          
          #send 100 coins to walleta
          genesisTransaction = txn.Transaction(Coinbase.PEMPublicKey.decode(), walletA.PEMPublicKey.decode(), 10000, 0, None)
          genesisTransaction.GenerateTransactionSignature(Coinbase.PrivateKey)
          
          #give the transaction a manual hash
          genesisTransaction.TransactionHash = "0"
          genesisTransaction.TransactionOutputs.append(outs.TransactionOutput(genesisTransaction.Recipient, genesisTransaction.Value, genesisTransaction.TransactionHash,0))
          self.UTXOs[genesisTransaction.TransactionOutputs[0].Id] = {"Transaction":genesisTransaction.TransactionOutputs[0]}
          
          print("create and mine genesis block")
          genesis = bl.Block("0")
          genesis.AddTransaction(genesisTransaction, self)
          self.AddBlock(genesis)
          
          #block 1
          block1 = bl.Block(genesis.BlockHash)
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("sending 40 from wallet a to b")
          block1.AddTransaction(walletA.SendFunds(walletB.PEMPublicKey.decode(), 40, self), self)
          self.AddBlock(block1)
          
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("balance of wallet b = " + str(walletB.getBalance(self)))

          #block 1
          block2 = bl.Block(block1.BlockHash)
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("spending more coins than in wallet")
          block2.AddTransaction(walletA.SendFunds(walletB.PEMPublicKey.decode(), 5, self), self)
          self.AddBlock(block2)
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("balance of wallet b = " + str(walletB.getBalance(self)))
          
          #block 1
          block3 = bl.Block(block2.BlockHash)
          print("balance of wallet a = " + str(walletB.getBalance(self)))
          print("sending 40 from wallet a to b")
          block3.AddTransaction(walletB.SendFunds(walletA.PEMPublicKey.decode(), 23.5, self), self)
          self.AddBlock(block3)
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("balance of wallet b = " + str(walletB.getBalance(self)))
          
          #clears spent Utxos and keeps the chain clean
          #self.CleanUpUtxo()
          self.CheckChainValid(genesisTransaction)
          
          #block 4 tests creating a new coin
          block4 = bl.Block(block3.BlockHash)
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("Creating a new coin")
          CoinTxn = walletA.CreateNewCoin(self, "HephCoin", "Heph", 100000)
          block4.AddTransaction(CoinTxn, self)
          self.AddBlock(block4)
          
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("coin balance of wallet a = " + str(walletA.GetTokenBalance(self, self.AlternativeCoins[0])))
          
          #block 5 sends tokens from one wallet to another
          block5 = bl.Block(block4.BlockHash)
          print("coin balance of wallet a = " + str(walletA.GetTokenBalance(self, self.AlternativeCoins[0])))
          print("coin balance of wallet b = " + str(walletB.GetTokenBalance(self, self.AlternativeCoins[0])))
          print("sending 500.5050505 Tokens from wallet a to b")
          TokenTransaction = walletA.SendToken(walletB.PEMPublicKey.decode(), 500.5050505, self.AlternativeCoins[0], self)
          block5.AddTransaction(TokenTransaction, self)
          self.AddBlock(block5)
          
          print("coin balance of wallet a = " + str(walletA.GetTokenBalance(self, self.AlternativeCoins[0])))
          print("coin balance of wallet b = " + str(walletB.GetTokenBalance(self, self.AlternativeCoins[0])))
          
          print("coin balance of wallet b = " + str(walletB.GetTokenBalance(self, self.AlternativeCoins[0])))
          print("Testing burning token by using the burn wallet function - This permenantly destroys the UTXOs")
          block6 = bl.Block(block5.BlockHash)
          BurnTransaction = walletB.BurnToken(0.5050505, self.AlternativeCoins[0], self)
          block6.AddTransaction(BurnTransaction, self)
          self.AddBlock(block6)
          
          print("spendable balance of wallet b = " + str(walletB.GetSpentableTokenBalance(self, self.AlternativeCoins[0])))
          print("freezing some 60 tokens from wallet b")
          block7 = bl.Block(block6.BlockHash)
          FreezeTransaction = walletB.FreezeUnfreezeTokens(60,self.AlternativeCoins[0], True, self)
          block7.AddTransaction(FreezeTransaction, self)
          self.AddBlock(block7)
          print("spentable token balance of wallet b = " + str(walletB.GetSpentableTokenBalance(self, self.AlternativeCoins[0])))
          print("coin balance of wallet b = " + str(walletB.GetTokenBalance(self, self.AlternativeCoins[0])))
          
          print("unfreezing 30 tokens")
          block8 = bl.Block(block7.BlockHash)
          FreezeTransaction = walletB.FreezeUnfreezeTokens(22,self.AlternativeCoins[0], False, self)
          block8.AddTransaction(FreezeTransaction, self)
          self.AddBlock(block8)
          print("spentable token balance of wallet b = " + str(walletB.GetSpentableTokenBalance(self, self.AlternativeCoins[0])))
          print("coin balance of wallet b = " + str(walletB.GetTokenBalance(self, self.AlternativeCoins[0])))
          
          print("Testing Limit Order")
          block9 = bl.Block(block8.BlockHash)
          order = walletB.CreateOrder(self.AlternativeCoins[0], 0.1, 100, True, self)
          block9.AddTransaction(order, self)
          self.AddBlock(block9)
          print("Buy Order Added")
          
          print("Testing Limit Order when matching order on the market")
          print("Values before Trade")
          
          print("coin balance of wallet a = " + str(walletA.GetTokenBalance(self, self.AlternativeCoins[0])))
          print("coin balance of wallet b = " + str(walletB.GetTokenBalance(self, self.AlternativeCoins[0])))
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("balance of wallet b = " + str(walletB.getBalance(self)))
          
          block10 = bl.Block(block9.BlockHash)
          order = walletA.CreateOrder(self.AlternativeCoins[0], 0.1, 10, False, self)
          block10.AddTransaction(order, self)
          self.AddBlock(block10)
          
          print("Balance After Trade")
          print("coin balance of wallet a = " + str(walletA.GetTokenBalance(self, self.AlternativeCoins[0])))
          print("coin balance of wallet b = " + str(walletB.GetTokenBalance(self, self.AlternativeCoins[0])))
          print("balance of wallet a = " + str(walletA.getBalance(self)))
          print("balance of wallet b = " + str(walletB.getBalance(self)))
          
          return self.UTXOs, self.OpenOrders
          
          
#     #clears spent transactions
#     def CleanUpUtxo(self):
#          
#          newUTXO = dict()
#          
#          for i in self.UTXOs:
#               
#               if self.UTXOs[i]['Transaction'].Spent == False:
#                    newUTXO[i] = {'Transaction':self.UTXOs[i]['Transaction']}
#          
#          self.UTXOs = newUTXO
#          
          
     
Heph = HephDex()
a, b = Heph.HexCoin()
