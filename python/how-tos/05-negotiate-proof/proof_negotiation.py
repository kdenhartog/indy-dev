"""
Example demonstrating Proof Verification.

First Issuer creates Claim Definition for existing Schema.
After that, it issues a Claim to Prover (as in issue_credential.py example)

Once Prover has successfully stored its Claim, it uses Proof Request that he
received, to get Claims which satisfy the Proof Request from his wallet.
Prover uses the output to create Proof, using its Master Secret.
After that, Proof is verified against the Proof Request
"""

import asyncio
import json
import pprint
import sys
import time

from src.utils import run_coroutine, get_pool_genesis_txn_path, PROTOCOL_VERSION

from indy import pool, ledger, wallet, did, anoncreds, crypto
from indy.error import IndyError


seq_no = 1
pool_name = 'pool'
wallet_credentials = json.dumps({"key": "wallet_key"})
steward_wallet_config = json.dumps({"id": "steward_wallet"})
issuer_wallet_config = json.dumps({"id": "issuer_wallet"})
pool_genesis_txn_path = get_pool_genesis_txn_path(pool_name)
pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})

def print_log(value_color="", value_noncolor=""):
    """set the colors for text."""
    HEADER = '\033[92m'
    ENDC = '\033[0m'
    print(HEADER + value_color + ENDC + str(value_noncolor))


async def proof_negotiation():
    try:
         # Set protocol version 2 to work with Indy Node 1.4
        await pool.set_protocol_version(PROTOCOL_VERSION)

        # 1.
        print_log('\n1. Creates a new local pool ledger configuration that is used '
                  'later when connecting to ledger.\n')
        await pool.create_pool_ledger_config(pool_name, pool_config)

        # 2.
        print_log('\n2. Open pool ledger and get handle from libindy\n')
        pool_handle = await pool.open_pool_ledger(pool_name, None)

        # 3.
        print_log('\n3. Creating new issuer, steward, and prover secure wallet\n')
        await wallet.create_wallet(issuer_wallet_config, wallet_credentials)
        await wallet.create_wallet(steward_wallet_config, wallet_credentials)

        # 4.
        print_log('\n4. Open wallet and get handle from libindy\n')
        issuer_wallet_handle = await wallet.open_wallet(issuer_wallet_config, wallet_credentials)
        steward_wallet_handle = await wallet.open_wallet(steward_wallet_config, wallet_credentials)

        # 5.
        print_log('\n5. Generating and storing steward DID and verkey\n')
        steward_seed = '000000000000000000000000Steward1'
        did_json = json.dumps({'seed': steward_seed})
        steward_did, steward_verkey = await did.create_and_store_my_did(steward_wallet_handle, did_json)
        print_log('Steward DID: ', steward_did)
        print_log('Steward Verkey: ', steward_verkey)

        # 6.
        print_log(
            '\n6. Generating and storing trust anchor (also issuer) DID and verkey\n')
        trust_anchor_did, trust_anchor_verkey = await did.create_and_store_my_did(issuer_wallet_handle, "{}")
        print_log('Trust anchor DID: ', trust_anchor_did)
        print_log('Trust anchor Verkey: ', trust_anchor_verkey)

        # 7.
        print_log('\n7. Building NYM request to add Trust Anchor to the ledger\n')
        nym_transaction_request = await ledger.build_nym_request(submitter_did=steward_did,
                                                                 target_did=trust_anchor_did,
                                                                 ver_key=trust_anchor_verkey,
                                                                 alias=None,
                                                                 role='TRUST_ANCHOR')
        print_log('NYM transaction request: ')
        pprint.pprint(json.loads(nym_transaction_request))

        # 8.
        print_log('\n8. Sending NYM request to the ledger\n')
        nym_transaction_response = await ledger.sign_and_submit_request(pool_handle=pool_handle,
                                                                        wallet_handle=steward_wallet_handle,
                                                                        submitter_did=steward_did,
                                                                        request_json=nym_transaction_request)
        print_log('NYM transaction response: ')
        pprint.pprint(json.loads(nym_transaction_response))

        
        (gvt_schema_id, gvt_schema) = await anoncreds.issuer_create_schema(trust_anchor_did, 'gvt', '1.0',
                                                                json.dumps(['age', 'sex', 'height', 'name']))
        schema_request = await ledger.build_schema_request(trust_anchor_did, gvt_schema)
        await ledger.sign_and_submit_request(pool_handle, issuer_wallet_handle, trust_anchor_did, schema_request)
        print_log('Create Schema and submiting to ledger')
        pprint.pprint(json.loads(schema_request))

        time.sleep(1)
        
        get_schema_request = await ledger.build_get_schema_request(trust_anchor_did, gvt_schema_id)
        get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
        (schema_id, gvt_schema_json) = await ledger.parse_get_schema_response(get_schema_response)

        # 11.
        print_log(
            '\n11. Creating and storing CRED DEFINITION using anoncreds as Trust Anchor, for the given Schema\n')
        cred_def_tag = 'cred_def_tag'
        cred_def_type = 'CL'
        cred_def_config = json.dumps({"support_revocation": False})

        (cred_def_id, cred_def_json) = await anoncreds.issuer_create_and_store_credential_def(issuer_wallet_handle, trust_anchor_did, gvt_schema_json, cred_def_tag, cred_def_type, cred_def_config)
        print_log('Credential definition: ')
        pprint.pprint(json.loads(cred_def_json))

        # 12.
        print_log('\n12. Creating Prover wallet and opening it to get the handle\n')
        prover_did = 'VsKV7grR1BUE29mG2Fm2kX'
        prover_wallet_config = json.dumps({"id": "prover_wallet"})
        prover_wallet_credentials = json.dumps({"key": "prover_wallet_key"})
        await wallet.create_wallet(prover_wallet_config, prover_wallet_credentials)
        prover_wallet_handle = await wallet.open_wallet(prover_wallet_config, prover_wallet_credentials)

        # 13.
        print_log('\n13. Prover is creating Master Secret\n')
        master_secret_name = 'master_secret'
        master_secret_id = await anoncreds.prover_create_master_secret(prover_wallet_handle, master_secret_name)

        # 14.
        print_log(
            '\n14. Issuer (Trust Anchor) is creating a Credential Offer for Prover\n')
        schema_json = json.dumps(gvt_schema)
        cred_offer_json = await anoncreds.issuer_create_credential_offer(issuer_wallet_handle, cred_def_id)
        print_log('Credential Offer: ')
        pprint.pprint(json.loads(cred_offer_json))

        # 15.
        print_log(
            '\n15. Prover creates Credential Request for the given credential offer\n')
        (cred_req_json, cred_req_metadata_json) = await anoncreds.prover_create_credential_req(prover_wallet_handle, prover_did, cred_offer_json, cred_def_json, master_secret_id)
        print_log('Credential Request: ')
        pprint.pprint(json.loads(cred_req_json))

        # 16.
        print_log(
            '\n16. Issuer (Trust Anchor) creates Credential for Credential Request\n')
        cred_values_json = json.dumps({
            'sex': ['male', '5944657099558967239210949258394887428692050081607692519917050011144233115103'],
            'name': ['Alex', '1139481716457488690172217916278103335'],
            'height': ['175', '175'],
            'age': ['28', '28']
        })
        (cred_json, _, _) = await anoncreds.issuer_create_credential(issuer_wallet_handle, cred_offer_json, cred_req_json, cred_values_json, None, None)
        print_log('Credential: ')
        pprint.pprint(json.loads(cred_json))

        # 17.
        print_log('\n17. Prover processes and stores Credential\n')
        await anoncreds.prover_store_credential(prover_wallet_handle, None, cred_req_metadata_json, cred_json, cred_def_json, None)


        # 18.
        print_log('\n18. Prover gets Claims for Proof Request\n')
        proof_request = {
            'nonce': '123432421212',
            'name': 'gvt',
            'version': '0.1',
            'requested_attributes': {
                'attr1_referent': {
                    'name': 'name'
                }
            },
            'requested_predicates': {
                'predicate1_referent': {
                    'name': 'age',
                    'p_type': '>=',
                    'p_value': 18,
                }
            }
        }
        #'restrictions': [{'issuer_did': trust_anchor_did}]
        print_log('Proof Request: ')
        pprint.pprint(proof_request)
        proof_req_json = json.dumps(proof_request)
        claims_for_proof_request_json = await anoncreds.prover_get_credentials_for_proof_req(prover_wallet_handle, \
                                                                                             proof_req_json)
        claims_for_proof_request = json.loads(claims_for_proof_request_json)
        print_log('Claims for Proof Request: ')
        pprint.pprint(claims_for_proof_request)

        # 19.
        print_log('\n19. Prover creates Proof for Proof Request\n')
        referent = claims_for_proof_request['attrs']['attr1_referent'][0]['cred_info']['referent']
        print_log('Referent: ')
        pprint.pprint(referent)
        requested_credentials_json = json.dumps({
            'self_attested_attributes': {},
            'requested_attributes': {
                'attr1_referent': {'cred_id': referent, 'revealed': True}
            },
            'requested_predicates': {
                'predicate1_referent': {'cred_id': referent}
            }
        })
        pprint.pprint(json.loads(requested_credentials_json))
    
        schemas_json = {}
        get_schema_request = await ledger.build_get_schema_request(prover_did, schema_id)
        get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
        (received_schema_id, received_schema) = await ledger.parse_get_schema_response(get_schema_response)
        schemas_json[received_schema_id] = json.loads(received_schema)
        
        # cred_defs_json = {}
        # c_def_id = json.loads(cred_def_json).get("id")
        # print(c_def_id)
        # get_cred_def_request = await ledger.build_get_cred_def_request(trust_anchor_did, c_def_id)
        # get_cred_def_response = await ledger.submit_request(pool_handle, get_cred_def_request)
        # (received_cred_def_id, received_cred_def) = await ledger.parse_get_cred_def_response(get_cred_def_response)
        # cred_defs_json[received_cred_def_id] = json.loads(received_cred_def)
        
        revoc_regs_json = json.dumps({})

        print("\n\n proof_req_json: " + proof_req_json + "\n\n")
        # print(requested_credentials_json + "\n\n")
        # print(master_secret_id + "\n\n")
        # print(schemas_json + "\n\n")
        # print(cdefs_json + "\n\n")
        # print(revoc_regs_json + "\n\n")

        proof_json = await anoncreds.prover_create_proof(prover_wallet_handle, proof_req_json, requested_credentials_json, master_secret_id, json.dumps(schemas_json), cred_def_json, revoc_regs_json)
        proof = json.loads(proof_json)
       
        #assert 'Alex' == proof['requested_proof']['revealed_attrs']['attr1_referent'][1]

        # 20.
        print_log('\n11.Verifier is verifying proof from Prover\n')
        #assert await anoncreds.verifier_verify_proof(proof_req_json, proof_json, schemas_json, claim_defs_json, revoc_regs_json)

        # 21
        print_log('\n12. Closing both wallet_handles\n')
        await wallet.close_wallet(issuer_wallet_handle)
        await wallet.close_wallet(prover_wallet_handle)

        # 22
        print_log('\n13. Deleting created wallet_handles\n')
        await wallet.delete_wallet(prover_wallet_name, wallet_credentials)
        await wallet.delete_wallet(issuer_wallet_name, wallet_credentials)

    except IndyError as e:
        print('Error occurred: %s' % e)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(proof_negotiation())
    loop.close()


if __name__ == '__main__':
    main()

