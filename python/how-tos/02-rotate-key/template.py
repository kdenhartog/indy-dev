"""
Example demonstrating how to do the key rotation on the ledger.

Steward already exists on the ledger and its DID/Verkey are obtained using seed.
Trust Anchor's DID/Verkey pair is generated and stored into wallet.
Stewards builds NYM request in order to add Trust Anchor to the ledger.
Once NYM transaction is done, Trust Anchor wants to change its Verkey.
First, temporary key is created in the wallet.
Second, Trust Anchor builds NYM request to replace the Verkey on the ledger.
Third, when NYM transaction succeeds, Trust Anchor makes new Verkey permanent in wallet
(it was only temporary before).

To assert the changes, Trust Anchor reads both the Verkey from the wallet and the Verkey from the ledger
using GET_NYM request, to make sure they are equal to the new Verkey, not the original one
added by Steward
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
wallet_config = json.dumps({"id": "wallet"})
wallet_credentials = json.dumps({"key": "wallet_key"})
pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})


def print_log(value_color="", value_noncolor=""):
    """set the colors for text."""
    HEADER = '\033[92m'
    ENDC = '\033[0m'
    print(HEADER + value_color + ENDC + str(value_noncolor))

async def rotate_key_on_the_ledger():
	try:
		await pool.set_protocol_version(PROTOCOL_VERSION)

		# Tell SDK which pool you are going to use. You should have already started
		# this pool using docker compose or similar. Here, we are dumping the config
		# just for demonstration purposes. This follows the same steps as the write-did-and-query-verkey
		# tutorial.
		print_log('1. Creates a new local pool ledger configuration that is used '
                    'later when connecting to ledger.\n')
		await pool.create_pool_ledger_config(config_name=pool_name, config=pool_config)

		print_log('\n2. Open pool ledger and get handle from libindy\n')
		pool_handle = await pool.open_pool_ledger(config_name=pool_name, config=None)

		print_log('\n3. Creating new secure wallet with the given unique name\n')
		await wallet.create_wallet(wallet_config, wallet_credentials)

		print_log('\n4. Open wallet and get handle from libindy to use in methods that require wallet access\n')
		wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)

		# First, put a steward DID and its keypair in the wallet. This doesn't write anything to the ledger,
		# but it gives us a key that we can use to sign a ledger transaction that we're going to submit later.
		print_log('\n5. Generating and storing steward DID and verkey\n')

		# The DID and public verkey for this steward key are already in the ledger; they were part of the genesis
		# transactions we told the SDK to start with in the previous step. But we have to also put the DID, verkey,
		# and private signing key into our wallet, so we can use the signing key to submit an acceptably signed
		# transaction to the ledger, creating our *next* DID (which is truly new). This is why we use a hard-coded seed
		# when creating this DID--it guarantees that the same DID and key material are created that the genesis txns
		# expect.
		steward_seed = "000000000000000000000000Steward1"

		did_json = json.dumps({'seed': steward_seed})

		steward_did, steward_verkey = await did.create_and_store_my_did(wallet_handle, did_json)
		print_log('Steward DID: ', steward_did)

		# Now, create a new DID and verkey for a trust anchor, and store it in our wallet as well. Don't use a seed;
		# this DID and its keys are secure and random. Again, we're not writing to the ledger yet.
		print_log('\n6. Generating and storing trust anchor DID and verkey\n')
		trust_anchor_did, trust_anchor_verkey = await did.create_and_store_my_did(wallet_handle, "{}")
		print_log('Trust Anchor DID: ', trust_anchor_did)
		print_log('Trust Anchor Verkey: ', trust_anchor_verkey)

		# Here, we are building the transaction payload that we'll send to write the Trust Anchor identity to the ledger.
		# We submit this transaction under the authority of the steward DID that the ledger already recognizes.
		# This call will look up the private key of the steward DID in our wallet, and use it to sign the transaction.
		print_log('\n7. Building NYM request to add Trust Anchor to the ledger\n')
		nym_transaction_request = await ledger.build_nym_request(submitter_did=steward_did,
                                                           target_did=trust_anchor_did,
                                                           ver_key=trust_anchor_verkey,
                                                           alias=None,
                                                           role='TRUST_ANCHOR')

		print_log('NYM request: ')
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

		print_log('NYM response: ')
		pprint.pprint(json.loads(nym_transaction_response))

		# At this point, we have successfully written a new identity to the ledger. Our next step will be to query it.


		# Step 3 code goes here.

       		# Here we are generating the new verkey and starting the process to rotate in the wallet
		print_log('\n9. Generating new verkey of trust anchor in wallet\n')
		new_verkey = await did.replace_keys_start(wallet_handle, trust_anchor_did, "{}")
		print_log('New Trust Anchor Verkey: ', new_verkey)

		# then we need to update the ledger so that others can find the updated key
		print_log('\n10. Building NYM request to update new verkey to ledger\n')
		nym_request = await ledger.build_nym_request(trust_anchor_did, trust_anchor_did, new_verkey, None, 'TRUST_ANCHOR')
		print_log('NYM request:')
		pprint.pprint(json.loads(nym_request))

		# now we sign the transaction so the ledger can validate the transaction
		print_log('\n11. Sending NYM request to the ledger\n')
		nym_response = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trust_anchor_did, nym_request)
		print_log('NYM response:')
		pprint.pprint(json.loads(nym_response))

		# This finishes the rotation of the key in the wallet
		print_log('\n12. Apply new verkey in wallet\n')
		await did.replace_keys_apply(wallet_handle, trust_anchor_did)


		# Step 4 code goes here.

       		# Check to make sure the key is updated now and exists in the wallet
		print_log('\n13. Reading new verkey from wallet\n')
		verkey_in_wallet = await did.key_for_local_did(wallet_handle, trust_anchor_did)
		print_log('Trust Anchor Verkey in wallet: ', verkey_in_wallet)

		# build a query to check to make sure the key on the ledger is updated
		# In this we're building and formatting the transaction using the
		# trust anchor did to make the
		print_log('\n14. Building GET_NYM request to get Trust Anchor verkey\n')
		get_nym_request = await ledger.build_get_nym_request(trust_anchor_did, trust_anchor_did)
		print_log('Get NYM request:')
		pprint.pprint(json.loads(get_nym_request))

		# Now we'll submit the transaction built and foramtted in step 14 to the ledger
		print_log('\n15. Sending GET_NYM request to ledger\n')
		get_nym_response_json = await ledger.submit_request(pool_handle, get_nym_request)
		get_nym_response = json.loads(get_nym_response_json)
		print_log('GET NYM response:')
		pprint.pprint(get_nym_response)

		# compare the keys to make sure what's in the wallet is the same as on ledger
		print_log('\n16. Comparing Trust Anchor verkeys: written by Steward (original), '
                    'current in wallet and current from ledger\n')
		print_log('Written by Steward: ', trust_anchor_verkey)
		print_log('Current in wallet: ', verkey_in_wallet)
		verkey_from_ledger = json.loads(get_nym_response['result']['data'])['verkey']
		print_log('Current from ledger: ', verkey_from_ledger)
		print_log('Matching: ', verkey_from_ledger ==
		          verkey_in_wallet != trust_anchor_verkey)

		# Do some cleanup.
		print_log('\n17. Closing wallet and pool\n')
		await wallet.close_wallet(wallet_handle)
		await pool.close_pool_ledger(pool_handle)

		print_log('\n18. Deleting created wallet\n')
		await wallet.delete_wallet(wallet_config, wallet_credentials)

		print_log('\n19. Deleting pool ledger config')
		await pool.delete_pool_ledger_config(pool_name)


	except IndyError as e:
		print('Error occurred: %s' % e)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rotate_key_on_the_ledger())
    loop.close()


if __name__ == '__main__':
    main()

