<img src="Images/1200px-University_of_Tehran_logo.svg.png" width="100" align="left" />

<img src="Images/fanni.png" width="100" align="right"/>


<h1 style="float:center;" align="center">Bitcoin Transactions</h1>
<h4 style="float:center;" align="center"><b> Mohsen Amjadi </b></h4>


<br>

# Section 1

In this project we want to interact with bitcoin network practically and make some transactions to fully understand the content of the course.

for our purpose we are going to use TestNet that developers of bitcoin do their experiments on this network.

in our first step we should generate an address for ourselves on the testnet.
so the first thing we need is to generate a private key so that we would have a pair of private and public key.

The first thing we need to do is to apply the ECDSA or Elliptic Curve Digital Signature Algorithm to our private key. An elliptic curve is a curve defined by the equation y² = x³ + ax + b with a chosen a and b. There is a whole family of such curves that are widely known and used. Bitcoin uses the secp256k1 curve.

Since bitcoin uses spec256k1 the only thing that we need to do is multiply it by the initial point in the curve by the private key to obtain the public key.

Next step is to convert the key to a byte array and hash it, first with SHA-256 then with RIPEMD-160. Then we prepend the hashed public key with 0x6f because the address generated is meant to be used in the testnet.

Then we just encode the key bytes to base58 and we have our Bitcoin address.

the address that I have first generated and used in the code is : mnDRW17zqsRT4ew6o4KTdsaXsqELf6uGfq

but I have ran the code for other purposes so the results of the codes below may be different with this address that I mentioned.

To create a WIF key from the private key bytes, first we prepend the byte \xEF to the wif, then append the private key bytes. After, append the checksum, that is the last 4 bytes of the double SHA-256 of the partial wif key that we already have calculated.

so here is my private key in WIF format :
93M8Ue7roWS3tPBpsSLGM3TUyZGhZg2CxuX9zxqYKnnZ9RzVo3x

and this is my address in base 58 encoding:
mnDRW17zqsRT4ew6o4KTdsaXsqELf6uGfq

## Q1

the difference between MainNet and TestNet addresses is that the address for the mainnet start with 1 but the address for the testnet start with m or n.

```python

import os
import hashlib


def sha256(data):
    digest = hashlib.new("sha256")
    digest.update(data)
    return digest.digest()


def ripemd160(x):
    d = hashlib.new("ripemd160")
    d.update(x)
    return d.digest()


def b58(data):
    B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    if data[0] == 0:
        return "1" + b58(data[1:])

    x = sum([v * (256 ** i) for i, v in enumerate(data[::-1])])
    ret = ""
    while x > 0:
        ret = B58[x % 58] + ret
        x = x // 58

    return ret


class Point:
    def __init__(self,
        x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        y=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
        p=2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1):
        self.x = x
        self.y = y
        self.p = p

    def __add__(self, other):
        return self.__radd__(other)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __rmul__(self, other):
        n = self
        q = None

        for i in range(256):
            if other & (1 << i):
                q = q + n
            n = n + n

        return q

    def __radd__(self, other):
        if other is None:
            return self
        x1 = other.x
        y1 = other.y
        x2 = self.x
        y2 = self.y
        p = self.p

        if self == other:
            l = pow(2 * y2 % p, p-2, p) * (3 * x2 * x2) % p
        else:
            l = pow(x1 - x2, p-2, p) * (y1 - y2) % p

        newX = (l ** 2 - x2 - x1) % p
        newY = (l * x2 - l * newX - y2) % p

        return Point(newX, newY)

    def toBytes(self):
        x = self.x.to_bytes(32, "big")
        y = self.y.to_bytes(32, "big")
        return b"\x04" + x + y


def getPublicKey(privkey):
    SPEC256k1 = Point()
    pk = int.from_bytes(privkey, "big")
    hash160 = ripemd160(sha256((SPEC256k1 * pk).toBytes()))
    address = b"\x6f" + hash160 # Test Net

    # 0x00 if the target network is the mainnet

    address = b58(address + sha256(sha256(address))[:4])
    return address


def getWif(privkey):
    wif = b"\xEF" + privkey
    wif = b58(wif + sha256(sha256(wif))[:4])
    return wif


randomBytes = os.urandom(32)
print("Address: " + getPublicKey(randomBytes))
print("Privkey: " + getWif(randomBytes))

```

## Q2

this is a simple code that I have written for generating vanity address that start with three character "moh" which is the first three characters of my name. but eventhough I made the code to work in parallel, due to my laptop is weak and it takes a long time to be generated, I have not generated the vanity address but by running this code it may be generated after a time.


```python
!pip install bitcoin
```

```python
import bitcoin
import random
import time
import sys
from multiprocessing import Process, Value

THREADS = 16

class vanitygen(Process):
    def _init_ (self, pattern):
        Process._init_(self)
        self.pattern = pattern

    def run(self):
        while 1:
            # generate the secret private key
            secret_key = bitcoin.random_key()

            # generate the address derived from private key
            address = bitcoin.privkey_to_address(secret_key)

            if address.startswith("1" + self.pattern): break

        print("Vanity address found: ", address)
        print("HEX private key: ", secret_key)

def pattern_mine():
    #Init worker threads
    workers = []
    for i in range(0,THREADS):
        worker = vanitygen("moh")
        worker.daemon = True
        workers.append(worker)
        worker.start()

start = time.time()
pattern_mine()
end = time.time() - start
print("Elapsed time: ", end)
```
```python
import bitcoin
import random
import time
import sys


def pattern_mine(pattern = "moh", startWith = True):
    secret_key = ""
    address = ""
    while 1:
        # generate the secret private key
        secret_key = bitcoin.random_key()

        # generate the address derived from private key
        address = bitcoin.privkey_to_address(secret_key)

        if bool(startWith):
            if address.startswith("1" + pattern): break
        else:
            if pattern in address: break

    print("Vanity address found: ", address)
    print("HEX private key: ", secret_key)

start = time.time()
pattern_mine()
end = time.time() - start
print("Elapsed time: ", end)
```

## Q3
Here in this question we have been asked to create segwit addresses.I have used python bitcoin-utils library to create such an address.

SegWit effectively separates, or segregates, the signature data, or witness data, from bitcoin transactions. Doing so enables a Bitcoin block to hold more transactions, which in turn, increases the network’s scalability.Bech32 is a bitcoin address that is fully compatible with SegWit. Many people refer to Bech32 addresses as bc1 addresses because their address strings always start with ‘bc1’.

Primarily, transactions that utilize SegWit are cheaper and significantly faster than traditional bitcoin transactions.

Because SegWit separates the signature data from a transaction, you can fit more transactions into an individual Bitcoin block. Doing so removes the seven transactions per second maximum that previously existed for Bitcoin’s throughput.

Fitting more transactions into each block also leads to lower fees for users. Fees on SegWit transactions are generally 25 to 40 percent lower than non-SegWit ones.

```python
!pip install bitcoin-utils
```

```python
from bitcoinutils.setup import setup
from bitcoinutils.script import Script
from bitcoinutils.keys import P2wpkhAddress, P2wshAddress, P2shAddress, PrivateKey, PublicKey

def main():
    setup('testnet')

    priv = PrivateKey.from_wif('93M8Ue7roWS3tPBpsSLGM3TUyZGhZg2CxuX9zxqYKnnZ9RzVo3x')

    # compressed is the default
    print("\nPrivate key WIF:", priv.to_wif(compressed=True))

    # get the public key
    pub = priv.get_public_key()

    # compressed is the default
    print("Public key:", pub.to_hex(compressed=True))

    # get address from public key
    address = pub.get_segwit_address()

    # print the address and hash - default is compressed address
    print("Native Address:", address.to_string())
    segwit_hash = address.to_hash()
    print("Segwit Hash:", segwit_hash)
    print("Segwit Version:", address.get_type())


if __name__ == "__main__":
    main()
```

# section 2
these python codes have been run seperately in different files but because of the importing issues I did not run these codes here, but here is my address and you can check the transactions of me in blockchain explorer.

address: mnDRW17zqsRT4ew6o4KTdsaXsqELf6uGfq
In this section we are going to deal with transactions by completing a starter source code that we have been given, and it is using python bitcoinlib library.

so our first step is to complete the source code. below is my first version of that:

```python
import bitcoin.wallet
from bitcoin.core import COIN, b2lx, serialize, x, lx, b2x
import utils as u
#from utils import *

from bitcoin.core.script import *

bitcoin.SelectParams("testnet")
my_private_key = bitcoin.wallet.CBitcoinSecret("93M8Ue7roWS3tPBpsSLGM3TUyZGhZg2CxuX9zxqYKnnZ9RzVo3x")
my_public_key = my_private_key.pub
my_address = bitcoin.wallet.P2PKHBitcoinAddress.from_pubkey(my_public_key)
destination_address = bitcoin.wallet.CBitcoinAddress('mnDRW17zqsRT4ew6o4KTdsaXsqELf6uGfq')


def P2PKH_scriptPubKey(address):
    # return address.to_scriptPubKey() 
    return [OP_DUP, OP_HASH160, address, OP_EQUALVERIFY, OP_CHECKSIG]

def P2PKH_scriptSig(txin, txout, txin_scriptPubKey):
    signature = u.create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey, my_private_key)

    return [signature, my_public_key]

def send_from_P2PKH_transaction(amount_to_send, txid_to_spend, utxo_index,
                                txout_scriptPubKey):
    txout = u.create_txout(amount_to_send, txout_scriptPubKey)

    txin_scriptPubKey = P2PKH_scriptPubKey(my_address)
    txin = u.create_txin(txid_to_spend, utxo_index)
    txin_scriptSig = P2PKH_scriptSig(txin, txout, txin_scriptPubKey)

    new_tx = u.create_signed_transaction(txin, txout, txin_scriptPubKey,
                                       txin_scriptSig)

    return u.broadcast_transaction(new_tx)


if __name__ == '__main__':
    amount_to_send = 0.01 
    txid_to_spend = ('8d0eedb5813d48a07705a49683dfa64b4adaa8471483adc3a36ae057fab090aa')
    utxo_index = 0

    print(my_address)
    print(my_public_key.hex())
    print(my_private_key.hex())
    txout_scriptPubKey = P2PKH_scriptPubKey(destination_address)
    response = send_from_P2PKH_transaction(amount_to_send, txid_to_spend, utxo_index, txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)

```

so you can see in P2PKH_scriptPubKey function I returned:

[OP_DUP, OP_HASH160, address, OP_EQUALVERIFY, OP_CHECKSIG]

that are operations of scriptpubkey, also we can return address.to_scriptPubKey() but because CScript is applying on operation somewhere in the code we don't use and we we just return those operations.

scriptPubKey is a locking script placed on the output of a Bitcoin transaction that requires certain conditions to be met in order for a recipient to spend his/her bitcoins; scriptPubKey is also known as PubKey Script outside of the Bitcoin code. Conversely, scriptSig is the unlocking script that satisfies the conditions placed on the output by the scriptPubKey, and  is what allows it to be spent; outside of code, scriptSig is also known as Signature scripts.

By joining the scriptSig and the scriptPubKey we have a complete P2PKH, whose function can be summarized as follows:

An issuer can only spend bitcoins that they have received at a public address they own. But to spend them, you must prove that that address really is yours. So you need to supply the correct public key and private key to unlock the expense.

Confirmed this point, the issuer sends to another address a certain amount of coins that cease to be his property to become the property of another user, who can only spend those coins following the same process.

so for the P2PKH_scriptSig function we just return [signature, my_public_key].

## MultiSig
now in this question we are going to generate three new addresses and make a transaction that is using multiple signatures.

our three public keys are generated from the three private keys as below:


priv1 = bitcoin.wallet.CBitcoinSecret("92Xm1FGvDYQssVPp4G4jDJ1t5NsssL2wczX1nJTFYfsDb2yQu6d")

priv2 = bitcoin.wallet.CBitcoinSecret("92pGkKhYM2LcfEGftUuP7AVa2Z9TW5ke8VjRFZRDnuSGnDkc6PB")

priv3 = bitcoin.wallet.CBitcoinSecret("91wKX692EH3nFcvunvyFbhPhV3ezNdjgLQzcFvsf4CEJcJ8gai1")

pub1 = priv1.pub
pub2 = priv2.pub
pub3 = priv3.pub

---------------------------------------------------------

for our purpose I have defined a new function for scriptPubKey process and called P2PKH_scriptPubKey_multisig.
so it returns [my_public_key, OP_CHECKSIGVERIFY, OP_2, p1, p2, p3, OP_3, OP_CHECKMULTISIG] that is the format for checking multi signature.

and I gave the three pub keys to this function and saved the output as txout_scriptPubKey :

txout_scriptPubKey = P2PKH_scriptPubKey_multisig(pub1,pub2,pub3)

```python

import bitcoin.wallet
from bitcoin.core import COIN, b2lx, serialize, x, lx, b2x
import utils as u
#from utils import *

from bitcoin.core.script import *



bitcoin.SelectParams("testnet")
my_private_key = bitcoin.wallet.CBitcoinSecret("93M8Ue7roWS3tPBpsSLGM3TUyZGhZg2CxuX9zxqYKnnZ9RzVo3x")
my_public_key = my_private_key.pub

priv1 = bitcoin.wallet.CBitcoinSecret("92Xm1FGvDYQssVPp4G4jDJ1t5NsssL2wczX1nJTFYfsDb2yQu6d")
priv2 = bitcoin.wallet.CBitcoinSecret("92pGkKhYM2LcfEGftUuP7AVa2Z9TW5ke8VjRFZRDnuSGnDkc6PB")
priv3 = bitcoin.wallet.CBitcoinSecret("91wKX692EH3nFcvunvyFbhPhV3ezNdjgLQzcFvsf4CEJcJ8gai1")


pub1 = priv1.pub
pub2 = priv2.pub
pub3 = priv3.pub

my_address = bitcoin.wallet.P2PKHBitcoinAddress.from_pubkey(my_public_key)
destination_address = bitcoin.wallet.CBitcoinAddress('mnDRW17zqsRT4ew6o4KTdsaXsqELf6uGfq')


def P2PKH_scriptPubKey(address):
    # return address.to_scriptPubKey() 
    return [OP_DUP, OP_HASH160, address, OP_EQUALVERIFY, OP_CHECKSIG]

def P2PKH_scriptPubKey_multisig(p1,p2,p3):
    return [my_public_key, OP_CHECKSIGVERIFY,
                           OP_2, p1, p2, p3, OP_3, OP_CHECKMULTISIG]

def P2PKH_scriptSig(txin, txout, txin_scriptPubKey):
    signature = u.create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey, my_private_key)

    return [signature, my_public_key]

def send_from_P2PKH_transaction(amount_to_send, txid_to_spend, utxo_index,
                                txout_scriptPubKey):
    txout = u.create_txout(amount_to_send, txout_scriptPubKey)

    txin_scriptPubKey = P2PKH_scriptPubKey(my_address)
    txin = u.create_txin(txid_to_spend, utxo_index)
    txin_scriptSig = P2PKH_scriptSig(txin, txout, txin_scriptPubKey)

    new_tx = u.create_signed_transaction(txin, txout, txin_scriptPubKey,
                                       txin_scriptSig)

    return u.broadcast_transaction(new_tx)


if __name__ == '__main__':
    amount_to_send = 0.01 
    txid_to_spend = ('8d0eedb5813d48a07705a49683dfa64b4adaa8471483adc3a36ae057fab090aa')
    utxo_index = 0

    print(my_address)
    print(my_public_key.hex())
    print(my_private_key.hex())
    txout_scriptPubKey = P2PKH_scriptPubKey_multisig(pub1,pub2,pub3)
    response = send_from_P2PKH_transaction(amount_to_send, txid_to_spend, utxo_index, txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
```


after making the transaction we should spend that and send the money to my address. so for our purpose, I have written the below code for spending that. 

```python
from sys import exit
from bitcoin.core.script import *

from utils import *
from transaction import *



def multisig_scriptSig(txin, txout, txin_scriptPubKey):
    bank_sig = u.create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey,
                                             my_private_key)
    cust1_sig = u.create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey,
                                             priv1)
    cust2_sig = u.create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey,
                                             priv2)
    cust3_sig = u.create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey,
                                             priv3)

    return [OP_0, cust2_sig, bank_sig]



def send_from_multisig_transaction(amount_to_send, txid_to_spend, utxo_index,
                                   txin_scriptPubKey, txout_scriptPubKey):
    txout = u.create_txout(amount_to_send, txout_scriptPubKey)

    txin = u.create_txin(txid_to_spend, utxo_index)
    txin_scriptSig = multisig_scriptSig(txin, txout, txin_scriptPubKey)

    new_tx = u.create_signed_transaction(txin, txout, txin_scriptPubKey,
                                       txin_scriptSig)

    return u.broadcast_transaction(new_tx)


if __name__ == '__main__':

    amount_to_send = 0.000111
    txid_to_spend = '8d0eedb5813d48a07705a49683dfa64b4adaa8471483adc3a36ae057fab090aa'
    utxo_index = 0


    txin_scriptPubKey = P2PKH_scriptPubKey_multisig(pub1,pub2,pub3)
    txout_scriptPubKey = P2PKH_scriptPubKey(my_address)

    response = send_from_multisig_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        txin_scriptPubKey, txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
```
