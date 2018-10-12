import json
import logging
from typing import Optional

from indy import anoncreds, crypto, did, ledger, pool, wallet, pairwise
from indy.error import ErrorCode, IndyError
from src.utils import get_pool_genesis_txn_path, run_coroutine, PROTOCOL_VERSION

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def run():
    logger.info("Getting started -> started")

    pool_name = 'pool1'
    logger.info("Open Pool Ledger: {}".format(pool_name))
    pool_genesis_txn_path = get_pool_genesis_txn_path(pool_name)
    print(pool_genesis_txn_path)
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    

    # Set protocol version 2 to work with Indy Node 1.4
    await pool.set_protocol_version(PROTOCOL_VERSION)

    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    pool_handle = await pool.open_pool_ledger(pool_name, None)

    logger.info("=================================")
    logger.info("=== Setting up Alice's Wallet ===")
    logger.info("---------------------------------")

    logger.info("\"Alice\" -> Create wallet")
    alice_wallet_config = json.dumps({"id": "alice_wallet"})
    alice_wallet_credentials = json.dumps({"key": "alice_wallet_key"})
    try:
        await wallet.create_wallet(alice_wallet_config, alice_wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass

    logger.info("=================================")
    logger.info("=== Setting up Bob's Wallet ===")
    logger.info("---------------------------------")

    logger.info("\"Bob\" -> Create wallet")
    bob_wallet_config = json.dumps({"id": "bob_wallet"})
    bob_wallet_credentials = json.dumps({"key": "bob_wallet_key"})
    try:
        await wallet.create_wallet(bob_wallet_config, bob_wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass

    
    
    
if __name__ == '__main__':
    run_coroutine(run)
    time.sleep(1)  # FIXME waiting for libindy thread complete