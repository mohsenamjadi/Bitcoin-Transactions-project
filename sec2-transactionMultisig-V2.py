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