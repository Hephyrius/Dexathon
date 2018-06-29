# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 05:43:35 2018

@author: Khera

node deals Proof of Stake, Consensus, and related stuff

for now all connected nodes are localhost, no big discovery functionality in this prototype
"""
import zmq
import random
from threading import Thread
import time
import zlib, pickle as pickle
import Transaction as txn
import Block as bl
class Node():
     
     DiscoveredNodes = dict()
     KnownNodes = []
     ThisSocket = 0
     context = ""
     socket = ""
     Listeners = []
     BroadCasts = []
     obs = []

     thread = ""
     nonce = 0
     
     #basic network constructor
     def __init__(self):
          
          self.DiscoveredNodes = dict()
          self.KnownNodes = []
          self.nonce = 0
          self.Listeners = []
          self.BroadCasts = []
          self.obs = []

          try:
               self.ThisSocket = 5555
               self.context = zmq.Context()
               self.socket = self.context.socket(zmq.REP)
               self.socket.bind("tcp://*:"+str(self.ThisSocket))
          except Exception as e:
               self.ThisSocket = random.randrange(5556,6000)
               self.context = zmq.Context()
               self.socket = self.context.socket(zmq.REP)
               self.socket.bind("tcp://*:"+str(self.ThisSocket))

          self.RegisterNode()
          self.thread = Thread(target = self.Listen)
          #self.thread.setDaemon(True)
          self.thread.start()
     
     #register a node by broadcasting to the main node on 5555
     def RegisterNode(self):

          if self.ThisSocket != 5555:
               ctx = zmq.Context()
               sk = ctx.socket(zmq.REQ)
               sk.connect("tcp://localhost:5555")
               sk.send(("tcp://*:"+str(self.ThisSocket)).encode())
     
     #register a node by broadcasting to the main node on 5555
     def SendDataMasterNode(self, data):

          if self.ThisSocket != 5555:
               ctx = zmq.Context()
               sk = ctx.socket(zmq.REQ)
               sk.connect("tcp://localhost:5555")
               sk.send(data)
     
          #send the new node to all nodes
     def SendDataToAll(self, data):
          for i in self.KnownNodes:
               k = i.replace("*", "localhost")
               k = k.replace("b'", "")
               k = k.replace("'", "")
               #print(k)
               ctx = zmq.Context()
               sk = ctx.socket(zmq.REQ)
               sk.connect(k)
               sk.send(data)
     #listen for new messages.
     def Listen(self):
          
          while True:
               try:
                    message = self.socket.recv()
                    #print(message)
                    if "tcp" in str(message):
                         if message.decode() not in self.KnownNodes:
                              #print("added to list")
                              self.KnownNodes.append(message.decode())
                              self.SendToAll(message.decode())
                              self.BroadCastKnownToNew(message.decode())
                              self.socket.send(b"acknowkedge")
                    else:
                         #self.obs.append(message)
                         self.obs.append(pickle.loads(message))
                         if self.ThisSocket == 5555:
                              
                              self.SendDataToAll(message)
                         print(len(self.obs))
                         print(self.obs[0])
                         self.lastOb = pickle.loads(message)
                         self.socket.send(b"acknowkedge")
                         
               except Exception as e:
                    self.socket.send(b"acknowkedge")
                    #print(e)
                    
     #send the new node to all nodes
     def SendToAll(self, message):
          for i in self.KnownNodes:
               k = i.replace("*", "localhost")
               k = k.replace("b'", "")
               k = k.replace("'", "")
               #print(k)
               ctx = zmq.Context()
               sk = ctx.socket(zmq.REQ)
               sk.connect(k)
               sk.send(str(message).encode())
     
     
     #share known nodes to the new node                    
     def BroadCastKnownToNew(self, newNode):
          ctx = zmq.Context()
          sk = ctx.socket(zmq.REQ)
          new = newNode.replace("*", "localhost" )
          sk.connect(new)
          
          for i in self.KnownNodes:
               
               k = i.replace("b'", "")
               k = k.replace("'", "")
               sk.send(str(k).encode())
                    

     #register a staked node to the network
     def RegisterStake(self, PublicKey, Address, Staked):
          
          self.DiscoveredNodes[Address] = {"Public":PublicKey, "Staked":Staked}
     
     def InitListeners(self):
          self.Listeners = []
          for i in self.DiscoveredNodes:
               ctx = zmq.Context()
               results_receiver = ctx.socket(zmq.PULL)
               results_receiver.bind(i)
               self.Listeners.append(results_receiver)
     
     def InitBroadcasts(self):
          self.BroadCasts = []
          for i in self.DiscoveredNodes:
               ctx = zmq.Context()
               broadcaster = ctx.socket(zmq.REQ)
               broadcaster.connect(i)
               self.BroadCasts.append(broadcaster)
     
     #randomly select a staking node
     def Election(self):
          
          total = 0
          percentages = []
          for i in self.DiscoveredNodes:
               
               total += self.DiscoveredNodes[i]['Staked']
          
          for i in self.DiscoveredNodes:
               
               percentages.append(self.DiscoveredNodes[i]['Staked']/total)
          
          r = random.uniform(0,1)
          bounds = []
          runningTotal = 0
          
          for i in percentages:
               runningTotal += i
               bounds.append(runningTotal)
          
          elected = 0
          
          for i in range(len(bounds)):
               
               if i == 0 and r < bounds[0]:
                    elected = i
                    break
#               elif i == len(bounds) and r<bounds[len(bounds-1)]:
#                    elected == i
               elif r > bounds[i-1] and r<bounds[i]:
                    elected = i
                    break
          
          count = 0
          node = ""
          for i in self.DiscoveredNodes:
               if count == elected:
                    node = self.DiscoveredNodes[i]
                    break
               else:
                    count = count+1
          
          return r, elected, count, node, percentages


