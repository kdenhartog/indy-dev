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

from indy import pool, ledger, wallet, did
from indy.error import IndyError
from src.utils import get_pool_genesis_txn_path


pool_name = 'pool'
genesis_file_path = get_pool_genesis_txn_path("pool")
wallet_config = json.dumps({"id": "wallet"})
wallet_credentials = json.dumps({"key": "wallet_key"})
# Set protocol version to 2 to work with the current version of Indy Node
PROTOCOL_VERSION = 2


def print_log(value_color="", value_noncolor=""):
    """set the colors for text."""
    HEADER = '\033[92m'
    ENDC = '\033[0m'
    print(HEADER + value_color + ENDC + str(value_noncolor))


async def write_nym_and_query_verkey():
    try:
        await pool.set_protocol_version(PROTOCOL_VERSION)
        # Tell SDK which pool you are going to use. You should have already started
        # this pool using docker compose or similar. Here, we are dumping the config
        # just for demonstration purposes.
        pool_config = json.dumps({'genesis_txn': str(genesis_file_path)})
        print_log('\n1. Create new pool ledger configuration to connect to ledger.\n')
        await pool.create_pool_ledger_config(config_name=pool_name, config=pool_config)

        print_log('\n2. Open ledger and get handle\n')
        pool_handle = await pool.open_pool_ledger(config_name=pool_name, config=None)

        print_log('\n3. Create new identity wallet\n')
        await wallet.create_wallet(wallet_config, wallet_credentials)

        print_log('\n4. Open identity wallet and get handle\n')
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)


        # Step 3 code 
        # First, put a steward DID and its keypair in the wallet. This doesn't write anything to the ledger,
        # but it gives us a key that we can use to sign a ledger transaction that we're going to submit later.
        print_log('\n5. Generate and store steward DID and verkey\n')
        # The DID and public verkey for this steward key are already in the ledger; they were part of the genesis
        # transactions we told the SDK to start with in the previous step. But we have to also put the DID, verkey,
        # and private signing key into our wallet, so we can use the signing key to submit an acceptably signed
        # transaction to the ledger, creating our *next* DID (which is truly new). This is why we use a hard-coded seed
        # when creating this DID--it guarantees that the same DID and key material are created that the genesis txns
        # expect.
        steward_seed = '000000000000000000000000Steward1'
        did_json = json.dumps({'seed': steward_seed})
        steward_did, steward_verkey = await did.create_and_store_my_did(wallet_handle, did_json)
        print_log('Steward DID: ', steward_did)
        print_log('Steward Verkey: ', steward_verkey)

        # Now, create a new DID and verkey for a trust anchor, and store it in our wallet as well. Don't use a seed;
        # this DID and its keyas are secure and random. Again, we're not writing to the ledger yet.
        print_log('\n6. Generating and storing trust anchor DID and verkey\n')
        trust_anchor_did, trust_anchor_verkey = await did.create_and_store_my_did(wallet_handle, "{}")
        print_log('Trust anchor DID: ', trust_anchor_did)
        print_log('Trust anchor Verkey: ', trust_anchor_verkey)


        # Step 4 code goes here.
        # Here, we are building the transaction payload that we'll send to write the Trust Anchor identity to the ledger.
        # We submit this transaction under the authority of the steward DID that the ledger already recognizes.
        # This call will look up the private key of the steward DID in our wallet, and use it to sign the transaction.
        print_log('\n7. Building NYM request to add Trust Anchor to the ledger\n')
        nym_transaction_request = await ledger.build_nym_request(submitter_did=steward_did,
                                                                 target_did=trust_anchor_did,
                                                                 ver_key=trust_anchor_verkey,
                                                                 alias=None,
                                                                 role='TRUST_ANCHOR')
        print_log('NYM transaction request: ')
        pprint.pprint(json.loads(nym_transaction_request))

        # Now that we have the transaction ready, send it. The building and the sending are separate steps because some
        # clients may want to prepare transactions in one piece of code (e.g., that has access to privileged backend systems),
        # and communicate with the ledger in a different piece of code (e.g., that lives outside the safe internal
        # network).
        print_log('\n8. Sending NYM request to the ledger\n')
        nym_transaction_response = await ledger.sign_and_submit_request(pool_handle=pool_handle,
                                                                        wallet_handle=wallet_handle,
                                                                        submitter_did=steward_did,
                                                                        request_json=nym_transaction_request)
        print_log('NYM transaction response: ')
        pprint.pprint(json.loads(nym_transaction_response))

        # At this point, we have successfully written a new identity to the ledger. Our next step will be to query it.


        # Step 5 code goes here.
                # Here we are creating a third DID. This one is never written to the ledger, but we do have to have it in the
        # wallet, because every request to the ledger has to be signed by some requester. By creating a DID here, we
        # are forcing the wallet to allocate a keypair and identity that we can use to sign the request that's going
        # to read the trust anchor's info from the ledger.
        print_log('\n9. Generating and storing DID and verkey representing a Client '
                  'that wants to obtain Trust Anchor Verkey\n')
        client_did, client_verkey = await did.create_and_store_my_did(wallet_handle, "{}")
        print_log('Client DID: ', client_did)
        print_log('Client Verkey: ', client_verkey)

        print_log('\n10. Building the GET_NYM request to query trust anchor verkey\n')
        get_nym_request = await ledger.build_get_nym_request(submitter_did=client_did,
                                                             target_did=trust_anchor_did)
        print_log('GET_NYM request: ')
        pprint.pprint(json.loads(get_nym_request))

        print_log('\n11. Sending the Get NYM request to the ledger\n')
        get_nym_response_json = await ledger.submit_request(pool_handle=pool_handle,
                                                           request_json=get_nym_request)
        get_nym_response = json.loads(get_nym_response_json)
        print_log('GET_NYM response: ')
        pprint.pprint(get_nym_response)

        # See whether we received the same info that we wrote the ledger in step 4.
        print_log('\n12. Comparing Trust Anchor verkey as written by Steward and as retrieved in GET_NYM '
                  'response submitted by Client\n')
        print_log('Written by Steward: ', trust_anchor_verkey)
        verkey_from_ledger = json.loads(get_nym_response['result']['data'])['verkey']
        print_log('Queried from ledger: ', verkey_from_ledger)
        print_log('Matching: ', verkey_from_ledger == trust_anchor_verkey)

        # Do some cleanup.
        print_log('\n13. Closing wallet and pool\n')
        await wallet.close_wallet(wallet_handle)
        await pool.close_pool_ledger(pool_handle)

        print_log('\n14. Deleting created wallet\n')
        await wallet.delete_wallet(wallet_config, wallet_credentials)

        print_log('\n15. Deleting pool ledger config\n')
        await pool.delete_pool_ledger_config(pool_name)



    except IndyError as e:
        print('Error occurred: %s' % e)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(write_nym_and_query_verkey())
    loop.close()


if __name__ == '__main__':
    main()

