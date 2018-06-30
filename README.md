# Author : Harnick Singh Khera | Github.com/Hephyrius

## Dexathon

Binance Dexathon Entry
The Dex Entry consists of a single implementation. 
Language : Python, Purpose: An implementation where rapid experimentation is at the core.

## Note From Creator:

The Dexathon was a really educational project/competition. As a single person entrant, I had to wear many hats and learn a lot of technologies that i hadn't worked with much if at all before. Especially networking... I hate Networking. If a few more hours where given, the Simulator would be working in a manner that is indestinguistable from a networked chain.
Overall the implementation covers a large area, I did end up losing site towards the end which lead to the size of the code balooning like crazy 

## Feature Status

(These can be seen in main.py and client.py)

### Core Functions

Transactions and Blocks : Working
Transaction Hashing : Working
Signing and Verifying : Working
Sending Native Coin : Working
Recieving Native Coin : Working

### Token Based

Creating New Tokens for a Fee : Working - See PyDex/Main.py
Freezing Tokens : Working - See PyDex/Main.py
Burning Tokens : Working - See PyDex/Main.py

### Dex Functions

Creating Limit Orders : Working - See PyDex/Main.py
Settling Limit Orders : Working -- with minor bugs - See PyDex/Main.py

### Consensus Based:
Node Networking : Semi-Working/Unfinished - See PyDex/Client.py
Consensus : Semi-Working/Unfinished - See PyDex/Simulator.py

## The structure of the entry is as follows

ReadMe.Md - This file!

PyDex/

PyDex/Block.py - Class implementation of a block

PyDex/chain.csv - Left over from earlier testing. This might become the save location for the blockchain when storing to the fs. still havent decided

PyDex/Client.py - This is the interactive client that should can be used. It combines the Node Functionality with the Core Blockchain Functionality that is tested in Main.py. It is essentially a hybrid of Main.py, Node.py and Wallet.py

PyDex/LocalNode.py - This class is used in the consensys-simulator version of the blockchain, in order to simulate a staked node that is creating or vetting blocks. 

PyDex/Main.py - This is the main test blockchain, used for testing features for a single node blockchain with no real consensus. All changes are tested here before being added to the client.py file. Check this out to see whats going on under the hood.

PyDex/NetworkedMain.py - leftover file from earlier prototyping, this is what client.py took over.

PyDex/Node.py - This class deals with networking functions as and when they are needed

PyDex/Simulator.py - This class is a last minute addition that aims to recreate/simulate the Client.py class without the added complexities that networking created. It has a simulated consensus that can be described as hybrid between BlockProducer and delegated POS

PyDex/Transaction.py - This class deals with creating and dealing with transactions

PyDex/TransactionInput.py - This is part of the UTXO model used

PyDex/TransactionOutput.py - This is part of the UTXO model used

PyDex/UtilFunctions.py - This is used to hash, sign, verify as well as other misc helper functions

PyDex/Wallet.py - This provides core crypto functions such as creating a keypair, creating different transaction types ect.

Truncated_Experiment/ - This folder a similar Structure as pydex shown above, but with some changes that reduced stability of client.py

## Key Features

* UTXO Model for underlying currency manipulations
* Hybrid UXTO Transaction Types used for different functionality
	* Type 0 - Native Coin Transfers
	* Type 1 - Creating a new Coin
	* Type 2 - Sending a Created Coin
	* Type 3 - Burn Token
	* Type 4 - Freeze/Unfreeze owned tokens
	* Type 5 - Limit Order
	
*Currently Masternode based. 

	* Idea was a Custom Mesh Consensus thats loosely based on DPOS.
	
		* Basically the model has a Master Node used for discovery and that is used for the first few blocks. once a set number of coins have been staked it switches to a stake based election system - I did this because I suck at networking and this became a hinderence when working on consensus!

### Further Explanations

* The entire message queing system needs to be looked at, it is a hack of a job  (I hate networking) so it does not work half the time!

## Requirements

* Python == 3.6
* zmq (pip install zmq)
* Cryptography (pip install Cryptography)

## Note 

* This Implementation is from scratch with some influence from several sources such as medium posts
* This Dexathon entry works in a consensus-less single node environment, a multi-node simulated network and a multi-node networked environment.
* Most of the Core functions (other than consensus) have been implemented in one of the three main chains [PyDex/Main.py, PyDex/Client.py, PyDex/Simulator.py]. So i hope some of my ideas are considered :D


