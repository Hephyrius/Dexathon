# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 21:44:31 2018

@author: Khera

Transaction input used within the UTXO model
"""

class TransactionInput():
     
     TransactionOutputId = ""
     UTXO = None
     
     def __init__(self, _TransactionOutputId):
          self.TransactionOutputId = _TransactionOutputId
          self.UTXO = None