"""
Example demonstrating how to add DID with the role of Trust Anchor to ledger.
Uses seed to obtain Steward's DID which already exists on the ledger.
Then it generates new DID/Verkey pair for Trust Anchor.
Using Steward's DID, NYM transaction request is built to add Trust Anchor's DID and Verkey
on the ledger with the role of Trust Anchor.
Once the NYM is successfully written on the ledger, it generates new DID/Verkey pair that represents
a client, which are used to create GET_NYM request to query the ledger and confirm Trust Anchor's Verkey.
For the sake of simplicity, a single wallet is used. In the real world scenario, three different wallets
would be used and DIDs would be exchanged using some channel of communication
"""

import asyncio
import json
import pprint
import time

from indy import pool, ledger, wallet, did
from indy.error import IndyError

from src.utils import run_coroutine, get_pool_genesis_txn_path, PROTOCOL_VERSION

pool_name = 'pool1'
pool_genesis_txn_path = get_pool_genesis_txn_path(pool_name)
wallet_name = json.dumps({"id": "wallet"})
wallet_credentials = json.dumps({"key": "wallet_key"})
pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})


def print_log(value_color="", value_noncolor=""):
    """set the colors for text."""
    HEADER = '\033[92m'
    ENDC = '\033[0m'
    print(HEADER + value_color + ENDC + str(value_noncolor))


async def write_nym_and_query_verkey():
    try:
        await pool.set_protocol_version(PROTOCOL_VERSION)
        # Step 2 code goes here.

        # Step 3 code goes here.

        # Step 4 code goes here.

        # Step 5 code goes here.

    except IndyError as e:
        print('Error occurred: %s' % e)


if __name__ == '__main__':
    run_coroutine(write_nym_and_query_verkey)
    time.sleep(1)  # FIXME waiting for libindy thread complete

