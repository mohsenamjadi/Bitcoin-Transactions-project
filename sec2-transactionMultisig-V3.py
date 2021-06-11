
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

