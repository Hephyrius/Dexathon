# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 02:56:37 2018

@author: Khera

class is responsible for utility functions such as hashing

"""

import hashlib


class UtilFunctions:
     
     
     def applySha256(self, _inputData):
          calculatedhash = hashlib.sha256(_inputData.encode())
          hex_dig = calculatedhash.hexdigest()
          
      #    return calculatedhash, hex_dig
          return hex_dig
     
     
     
