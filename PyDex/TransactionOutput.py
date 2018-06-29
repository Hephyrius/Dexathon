# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 21:47:25 2018

@author: Khera

Transaction output used in UTXO model
"""
import UtilFunctions as utils
class TransactionOutput():
     
     Id = ""
     Recipient = ""
     Value = 0
     ParentTransactionId = ""
     Spent = False
     
     #function used to make sure that the recipients and pkey are the same
     def __init__(self, _recipient, _value, _parentTransactionId):
          self.Recipient = _recipient
          self.Value = _value
          self.ParentTransactionId = _parentTransactionId
          self.Id = utils.UtilFunctions.applySha256(utils.UtilFunctions, str(self.Recipient)+"_"+str(self.Value)+"_"+str(self.ParentTransactionId))
          self.Spent = False
     
     #function used to make sure that the recipients and pkey are the same
     def isSamePublicKey(self, _PublicKey):
          return (self.Recipient == _PublicKey)