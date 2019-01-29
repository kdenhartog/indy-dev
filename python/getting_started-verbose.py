import time

from indy import anoncreds, crypto, did, ledger, pool, wallet

import json
import logging
from typing import Optional

from indy.error import ErrorCode, IndyError

from src.utils import get_pool_genesis_txn_path, run_coroutine, PROTOCOL_VERSION

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def run():
    logger.info("0.0.0 Getting started -> started")

    pool_name = 'pool1'
    logger.info("0.0.1 Open Pool Ledger: {}".format(pool_name))
    pool_genesis_txn_path = get_pool_genesis_txn_path(pool_name)
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    print("Pool Config: " + pool_config)
    

    # Set protocol version 2 to work with Indy Node 1.4
    await pool.set_protocol_version(PROTOCOL_VERSION)

    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    pool_handle = await pool.open_pool_ledger(pool_name, None)

    logger.info("==============================")
    logger.info("1.0.0 === Getting Trust Anchor credentials for Faber, Acme, Thrift and Government  ==")
    logger.info("------------------------------")

    logger.info("1.0.1 \"Sovrin Steward\" -> Create wallet")
    steward_wallet_config = json.dumps({"id": "sovrin_steward_wallet"})
    steward_wallet_credentials = json.dumps({"key": "steward_wallet_key"})
    try:
        await wallet.create_wallet(steward_wallet_config, steward_wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass

    steward_wallet = await wallet.open_wallet(steward_wallet_config, steward_wallet_credentials)
    #print("Steward Sovin wallet: " + steward_wallet)

    logger.info("1.0.2 \"Sovrin Steward\" -> Create and store in Wallet DID from seed")
    steward_did_info = {'seed': '000000000000000000000000Steward1'}
    (steward_did, steward_key) = await did.create_and_store_my_did(steward_wallet, json.dumps(steward_did_info))
    print("Sovrin Steward DID: " + steward_did)

    logger.info("==============================")
    logger.info("1.1.0 == Getting Trust Anchor credentials - Government Onboarding  ==")
    logger.info("------------------------------")

    government_wallet_config = json.dumps({"id": "government_wallet"})
    government_wallet_credentials = json.dumps({"key": "government_wallet_key"})
    government_wallet, steward_government_key, government_steward_did, government_steward_key, _ \
        = await onboarding("1.1", pool_handle, "Sovrin Steward", steward_wallet, steward_did, 
                        "Government", None, government_wallet_config, government_wallet_credentials)
    #print("Government wallet: " + government_wallet)
    print("Government Sovrin Steward DID: " + government_steward_did)

    logger.info("==============================")
    logger.info("1.1.0 == Getting Trust Anchor credentials - Government getting Verinym  ==")
    logger.info("------------------------------")

    government_did = await get_verinym("1.1", pool_handle, "Sovrin Steward", steward_wallet, steward_did,
                                       steward_government_key, "Government", government_wallet, government_steward_did,
                                       government_steward_key, 'TRUST_ANCHOR')
    print("Government DID: " + government_did)

    logger.info("==============================")
    logger.info("1.2.0 == Getting Trust Anchor credentials - Faber Onboarding  ==")
    logger.info("------------------------------")

    faber_wallet_config = json.dumps({"id": "faber_wallet"})
    faber_wallet_credentials = json.dumps({"key": "faber_wallet_key"})
    faber_wallet, steward_faber_key, faber_steward_did, faber_steward_key, _ = \
        await onboarding("1.2", pool_handle, "Sovrin Steward", steward_wallet, steward_did, 
                        "Faber", None, faber_wallet_config, faber_wallet_credentials)
    #print("Faber wallet: " + faber_wallet)
    print("Faber Sovrin Steward DID: " + faber_steward_did)

    logger.info("==============================")
    logger.info("1.2.0 == Getting Trust Anchor credentials - Faber getting Verinym  ==")
    logger.info("------------------------------")

    faber_did = await get_verinym("1.2", pool_handle, "Sovrin Steward", steward_wallet, steward_did, steward_faber_key,
                                  "Faber", faber_wallet, faber_steward_did, faber_steward_key, 'TRUST_ANCHOR')
    print("Faber DID: " + faber_did)

    logger.info("==============================")
    logger.info("1.3.0 == Getting Trust Anchor credentials - Acme Onboarding  ==")
    logger.info("------------------------------")

    acme_wallet_config = json.dumps({"id": "acme_wallet"})
    acme_wallet_credentials = json.dumps({"key": "acme_wallet_key"})
    acme_wallet, steward_acme_key, acme_steward_did, acme_steward_key, _ = \
        await onboarding("1.3", pool_handle, "Sovrin Steward", steward_wallet, steward_did, 
                        "Acme", None, acme_wallet_config, acme_wallet_credentials)
    #print("Acme wallet: " + acme_wallet)
    print("Acme Sovrin Steward DID: " + acme_steward_did)           

    logger.info("==============================")
    logger.info("1.3.0 == Getting Trust Anchor credentials - Acme getting Verinym  ==")
    logger.info("------------------------------")

    acme_did = await get_verinym("1.3", pool_handle, "Sovrin Steward", steward_wallet, steward_did, steward_acme_key,
                                 "Acme", acme_wallet, acme_steward_did, acme_steward_key, 'TRUST_ANCHOR')
    print("Acme DID: " + acme_did)

    logger.info("==============================")
    logger.info("1.4.0 == Getting Trust Anchor credentials - Thrift Onboarding  ==")
    logger.info("------------------------------")

    thrift_wallet_config = json.dumps({"id": " thrift_wallet"})
    thrift_wallet_credentials = json.dumps({"key": "thrift_wallet_key"})
    thrift_wallet, steward_thrift_key, thrift_steward_did, thrift_steward_key, _ = \
        await onboarding("1.4", pool_handle, "Sovrin Steward", steward_wallet, steward_did, 
                        "Thrift", None, thrift_wallet_config, thrift_wallet_credentials)
    #print("Thrift wallet: " + thrift_wallet)
    print("Thrift Sovrin Steward DID: " + thrift_steward_did)

    logger.info("==============================")
    logger.info("1.4.0 == Getting Trust Anchor credentials - Thrift getting Verinym  ==")
    logger.info("------------------------------")

    thrift_did = await get_verinym("1.4", pool_handle, "Sovrin Steward", steward_wallet, steward_did, steward_thrift_key,
                                   "Thrift", thrift_wallet, thrift_steward_did, thrift_steward_key, 'TRUST_ANCHOR')
    print("Thrift DID: " + thrift_did)

    logger.info("==============================")
    logger.info("2.1.0 === Credential Schemas Setup ==")
    logger.info("------------------------------")

    logger.info("2.1.1 \"Government\" -> Create \"Job Certificate\" Schema")
    (job_certificate_schema_id, job_certificate_schema) = \
        await anoncreds.issuer_create_schema(government_did, 'Job-Certificate', '0.2',
                                             json.dumps(['first_name', 'last_name', 'salary', 'employee_status',
                                                         'experience']))
    print("Created Job Certificate schema using Government DID: " + government_did)
    print("Job Certificate schema id: " + job_certificate_schema_id)
    print("Job Certificate schema: " + job_certificate_schema)

    logger.info("2.1.2 \"Government\" -> Send \"Job Certificate\" Schema to Ledger")
    await send_schema(pool_handle, government_wallet, government_did, job_certificate_schema)

    logger.info("2.2.1 \"Government\" -> Create \"Transcript\" Schema")
    (transcript_schema_id, transcript_schema) = \
        await anoncreds.issuer_create_schema(government_did, 'Transcript', '1.2',
                                             json.dumps(['first_name', 'last_name', 'degree', 'status',
                                                         'year', 'average', 'ssn']))
    print("Created Transcript schema using Government DID: " + government_did)
    print("Transcript schema id: " + transcript_schema_id)
    print("Transcript schema: " + transcript_schema)

    logger.info("2.2.2 \"Government\" -> Send \"Transcript\" Schema to Ledger")
    await send_schema(pool_handle, government_wallet, government_did, transcript_schema)

    time.sleep(1)  # sleep 1 second before getting schema

    logger.info("==============================")
    logger.info("2.3.0 === Faber Credential Definition Setup ==")
    logger.info("------------------------------")

    logger.info("2.3.1 \"Faber\" -> Get \"Transcript\" Schema from Ledger")
    (_, transcript_schema) = await get_schema(pool_handle, faber_did, transcript_schema_id)

    logger.info("2.3.2 \"Faber\" -> Create and store in Wallet \"Faber Transcript\" Credential Definition")
    (faber_transcript_cred_def_id, faber_transcript_cred_def_json) = \
        await anoncreds.issuer_create_and_store_credential_def(faber_wallet, faber_did, transcript_schema,
                                                               'TAG1', 'CL', '{"support_revocation": false}')
    print("Created Transcript credential definition using Faber DID: " + faber_did)
    print("Transcript credential definition id: " + faber_transcript_cred_def_id)
    print("Transcript credential definition: " + faber_transcript_cred_def_json)

    logger.info("2.3.3 \"Faber\" -> Send  \"Faber Transcript\" Credential Definition to Ledger")
    await send_cred_def(pool_handle, faber_wallet, faber_did, faber_transcript_cred_def_json)

    logger.info("==============================")
    logger.info("2.4.0 === Acme Credential Definition Setup ==")
    logger.info("------------------------------")

    logger.info("2.4.1 \"Acme\" -> Get from Ledger \"Job Certificate\" Schema")
    (_, job_certificate_schema) = await get_schema(pool_handle, acme_did, job_certificate_schema_id)

    logger.info("2.4.2 \"Acme\" -> Create and store in Wallet \"Acme Job Certificate\" Credential Definition")
    (acme_job_certificate_cred_def_id, acme_job_certificate_cred_def_json) = \
        await anoncreds.issuer_create_and_store_credential_def(acme_wallet, acme_did, job_certificate_schema,
                                                               'TAG1', 'CL', '{"support_revocation": false}')
    print("Created Job Certificate credential definition using Acme DID: " + acme_did)
    print("Job Certificate credential definition id: " + acme_job_certificate_cred_def_id)
    print("Job Certificate credential definition: " + acme_job_certificate_cred_def_json)

    logger.info("2.4.3 \"Acme\" -> Send \"Acme Job Certificate\" Credential Definition to Ledger")
    await send_cred_def(pool_handle, acme_wallet, acme_did, acme_job_certificate_cred_def_json)

    logger.info("==============================")
    logger.info("3.0.0 === Getting Transcript with Faber ==")
    logger.info("==============================")
    logger.info("3.1.0 == Getting Transcript with Faber - Onboarding ==")
    logger.info("------------------------------")

    alice_wallet_config = json.dumps({"id": " alice_wallet"})
    alice_wallet_credentials = json.dumps({"key": "alice_wallet_key"})
    alice_wallet, faber_alice_key, alice_faber_did, alice_faber_key, faber_alice_connection_response \
        = await onboarding("3.1", pool_handle, "Faber", faber_wallet, faber_did, 
                        "Alice", None, alice_wallet_config, alice_wallet_credentials)
    #print("Alice wallet: " + alice_wallet)
    print("Alice Faber DID: " + alice_faber_did) 

    logger.info("==============================")
    logger.info("3.2.0 == Getting Transcript with Faber - Getting Transcript Credential ==")
    logger.info("------------------------------")

    logger.info("3.2.1 \"Faber\" -> Create \"Transcript\" Credential Offer for Alice")
    transcript_cred_offer_json = \
        await anoncreds.issuer_create_credential_offer(faber_wallet, faber_transcript_cred_def_id)
    print("Transcript credential offer: " + transcript_cred_offer_json)

    logger.info("3.2.2 \"Faber\" -> Get key for Alice did")
    alice_faber_verkey = await did.key_for_did(pool_handle, acme_wallet, faber_alice_connection_response['did'])

    logger.info("3.2.3 \"Faber\" -> Authcrypt \"Transcript\" Credential Offer for Alice")
    authcrypted_transcript_cred_offer = await crypto.auth_crypt(faber_wallet, faber_alice_key, alice_faber_verkey,
                                                                transcript_cred_offer_json.encode('utf-8'))

    logger.info("3.2.4 \"Faber\" -> Send authcrypted \"Transcript\" Credential Offer to Alice (simulated)")

    logger.info("3.2.5 \"Alice\" -> Authdecrypted \"Transcript\" Credential Offer from Faber")
    faber_alice_verkey, authdecrypted_transcript_cred_offer_json, authdecrypted_transcript_cred_offer = \
        await auth_decrypt(alice_wallet, alice_faber_key, authcrypted_transcript_cred_offer)

    logger.info("3.2.6 \"Alice\" -> Create and store \"Alice\" Master Secret in Wallet")
    alice_master_secret_id = await anoncreds.prover_create_master_secret(alice_wallet, None)

    logger.info("3.2.7 \"Alice\" -> Get \"Faber Transcript\" Credential Definition from Ledger")
    (faber_transcript_cred_def_id, faber_transcript_cred_def) = \
        await get_cred_def(pool_handle, alice_faber_did, authdecrypted_transcript_cred_offer['cred_def_id'])
    print("Transcript credential definition id: " + faber_transcript_cred_def_id)
    print("Transcript credential definition: " + faber_transcript_cred_def)

    logger.info("3.2.8 \"Alice\" -> Create \"Transcript\" Credential Request for Faber")
    (transcript_cred_request_json, transcript_cred_request_metadata_json) = \
        await anoncreds.prover_create_credential_req(alice_wallet, alice_faber_did,
                                                     authdecrypted_transcript_cred_offer_json,
                                                     faber_transcript_cred_def, alice_master_secret_id)
    print("Transcript credential request: " + transcript_cred_request_json)
    print("Transcript credential request metadata: " + transcript_cred_request_metadata_json)

    logger.info("3.2.9 \"Alice\" -> Authcrypt \"Transcript\" Credential Request for Faber")
    authcrypted_transcript_cred_request = await crypto.auth_crypt(alice_wallet, alice_faber_key, faber_alice_verkey,
                                                                  transcript_cred_request_json.encode('utf-8'))

    logger.info("3.2.10 \"Alice\" -> Send authcrypted \"Transcript\" Credential Request to Faber (simulated)")

    logger.info("3.2.11 \"Faber\" -> Authdecrypt \"Transcript\" Credential Request from Alice")
    alice_faber_verkey, authdecrypted_transcript_cred_request_json, _ = \
        await auth_decrypt(faber_wallet, faber_alice_key, authcrypted_transcript_cred_request)

    logger.info("3.2.12 \"Faber\" -> Create \"Transcript\" Credential for Alice")
    transcript_cred_values = json.dumps({
        "first_name": {"raw": "Alice", "encoded": "1139481716457488690172217916278103335"},
        "last_name": {"raw": "Garcia", "encoded": "5321642780241790123587902456789123452"},
        "degree": {"raw": "Bachelor of Science, Marketing", "encoded": "12434523576212321"},
        "status": {"raw": "graduated", "encoded": "2213454313412354"},
        "ssn": {"raw": "123-45-6789", "encoded": "3124141231422543541"},
        "year": {"raw": "2015", "encoded": "2015"},
        "average": {"raw": "5", "encoded": "5"}
    })
    transcript_cred_json, _, _ = \
        await anoncreds.issuer_create_credential(faber_wallet, transcript_cred_offer_json,
                                                 authdecrypted_transcript_cred_request_json,
                                                 transcript_cred_values, None, None)
    print("Transcript credential: " + transcript_cred_json)

    logger.info("3.2.13 \"Faber\" -> Authcrypt \"Transcript\" Credential for Alice")
    authcrypted_transcript_cred_json = await crypto.auth_crypt(faber_wallet, faber_alice_key, alice_faber_verkey,
                                                               transcript_cred_json.encode('utf-8'))

    logger.info("3.2.14 \"Faber\" -> Send authcrypted \"Transcript\" Credential to Alice (simulated)")

    logger.info("3.2.15 \"Alice\" -> Authdecrypted \"Transcript\" Credential from Faber")
    _, authdecrypted_transcript_cred_json, _ = \
        await auth_decrypt(alice_wallet, alice_faber_key, authcrypted_transcript_cred_json)

    logger.info("3.2.16 \"Alice\" -> Store \"Transcript\" Credential from Faber")
    await anoncreds.prover_store_credential(alice_wallet, None, transcript_cred_request_metadata_json,
                                            authdecrypted_transcript_cred_json, faber_transcript_cred_def, None)

    logger.info("==============================")
    logger.info("4.1.0 === Apply for the job with Acme ==")
    logger.info("==============================")
    logger.info("4.1.0 == Apply for the job with Acme - Onboarding ==")
    logger.info("------------------------------")

    alice_wallet, acme_alice_key, alice_acme_did, alice_acme_key, acme_alice_connection_response = \
        await onboarding("4.1", pool_handle, "Acme", acme_wallet, acme_did, 
                        "Alice", alice_wallet, alice_wallet_config, alice_wallet_credentials)

    logger.info("==============================")
    logger.info("4.2.0 == Apply for the job with Acme - Transcript proving ==")
    logger.info("------------------------------")

    logger.info("4.2.1 \"Acme\" -> Create \"Job-Application\" Proof Request")
    job_application_proof_request_json = json.dumps({
        'nonce': '1432422343242122312411212',
        'name': 'Job-Application',
        'version': '0.1',
        'requested_attributes': {
            'attr1_referent': {
                'name': 'first_name'
            },
            'attr2_referent': {
                'name': 'last_name'
            },
            'attr3_referent': {
                'name': 'degree',
                'restrictions': [{'cred_def_id': faber_transcript_cred_def_id}]
            },
            'attr4_referent': {
                'name': 'status',
                'restrictions': [{'cred_def_id': faber_transcript_cred_def_id}]
            },
            'attr5_referent': {
                'name': 'ssn',
                'restrictions': [{'cred_def_id': faber_transcript_cred_def_id}]
            },
            'attr6_referent': {
                'name': 'phone_number'
            }
        },
        'requested_predicates': {
            'predicate1_referent': {
                'name': 'average',
                'p_type': '>=',
                'p_value': 4,
                'restrictions': [{'cred_def_id': faber_transcript_cred_def_id}]
            }
        }
    })

    logger.info("4.2.2 \"Acme\" -> Get key for Alice did")
    alice_acme_verkey = await did.key_for_did(pool_handle, acme_wallet, acme_alice_connection_response['did'])

    logger.info("4.2.3 \"Acme\" -> Authcrypt \"Job-Application\" Proof Request for Alice")
    authcrypted_job_application_proof_request_json = \
        await crypto.auth_crypt(acme_wallet, acme_alice_key, alice_acme_verkey,
                                job_application_proof_request_json.encode('utf-8'))

    logger.info("4.2.4 \"Acme\" -> Send authcrypted \"Job-Application\" Proof Request to Alice (simulated)")

    logger.info("4.2.5 \"Alice\" -> Authdecrypt \"Job-Application\" Proof Request from Acme")
    acme_alice_verkey, authdecrypted_job_application_proof_request_json, _ = \
        await auth_decrypt(alice_wallet, alice_acme_key, authcrypted_job_application_proof_request_json)

    logger.info("4.2.6 \"Alice\" -> Get credentials for \"Job-Application\" Proof Request")

    search_for_job_application_proof_request = \
        await anoncreds.prover_search_credentials_for_proof_req(alice_wallet,
                                                                authdecrypted_job_application_proof_request_json, None)

    cred_for_attr1 = await get_credential_for_referent(search_for_job_application_proof_request, 'attr1_referent')
    cred_for_attr2 = await get_credential_for_referent(search_for_job_application_proof_request, 'attr2_referent')
    cred_for_attr3 = await get_credential_for_referent(search_for_job_application_proof_request, 'attr3_referent')
    cred_for_attr4 = await get_credential_for_referent(search_for_job_application_proof_request, 'attr4_referent')
    cred_for_attr5 = await get_credential_for_referent(search_for_job_application_proof_request, 'attr5_referent')
    cred_for_predicate1 = \
        await get_credential_for_referent(search_for_job_application_proof_request, 'predicate1_referent')

    await anoncreds.prover_close_credentials_search_for_proof_req(search_for_job_application_proof_request)

    creds_for_job_application_proof = {cred_for_attr1['referent']: cred_for_attr1,
                                       cred_for_attr2['referent']: cred_for_attr2,
                                       cred_for_attr3['referent']: cred_for_attr3,
                                       cred_for_attr4['referent']: cred_for_attr4,
                                       cred_for_attr5['referent']: cred_for_attr5,
                                       cred_for_predicate1['referent']: cred_for_predicate1}

    schemas_json, cred_defs_json, revoc_states_json = \
        await prover_get_entities_from_ledger("4.2", pool_handle, alice_faber_did, creds_for_job_application_proof, 'Alice')

    logger.info("4.2.9 \"Alice\" -> Create \"Job-Application\" Proof")
    job_application_requested_creds_json = json.dumps({
        'self_attested_attributes': {
            'attr1_referent': 'Alice',
            'attr2_referent': 'Garcia',
            'attr6_referent': '123-45-6789'
        },
        'requested_attributes': {
            'attr3_referent': {'cred_id': cred_for_attr3['referent'], 'revealed': True},
            'attr4_referent': {'cred_id': cred_for_attr4['referent'], 'revealed': True},
            'attr5_referent': {'cred_id': cred_for_attr5['referent'], 'revealed': True},
        },
        'requested_predicates': {'predicate1_referent': {'cred_id': cred_for_predicate1['referent']}}
    })

    job_application_proof_json = \
        await anoncreds.prover_create_proof(alice_wallet, authdecrypted_job_application_proof_request_json,
                                            job_application_requested_creds_json, alice_master_secret_id,
                                            schemas_json, cred_defs_json, revoc_states_json)

    logger.info("4.2.10 \"Alice\" -> Authcrypt \"Job-Application\" Proof for Acme")
    authcrypted_job_application_proof_json = await crypto.auth_crypt(alice_wallet, alice_acme_key, acme_alice_verkey,
                                                                     job_application_proof_json.encode('utf-8'))

    logger.info("4.2.11 \"Alice\" -> Send authcrypted \"Job-Application\" Proof to Acme (simulated)")

    logger.info("4.2.12 \"Acme\" -> Authdecrypted \"Job-Application\" Proof from Alice")
    _, decrypted_job_application_proof_json, decrypted_job_application_proof = \
        await auth_decrypt(acme_wallet, acme_alice_key, authcrypted_job_application_proof_json)

    schemas_json, cred_defs_json, revoc_ref_defs_json, revoc_regs_json = \
        await verifier_get_entities_from_ledger("4.2", pool_handle, acme_did,
                                                decrypted_job_application_proof['identifiers'], 'Acme')

    logger.info("4.2.15 \"Acme\" -> Verify \"Job-Application\" Proof from Alice")
    assert 'Bachelor of Science, Marketing' == \
           decrypted_job_application_proof['requested_proof']['revealed_attrs']['attr3_referent']['raw']
    assert 'graduated' == \
           decrypted_job_application_proof['requested_proof']['revealed_attrs']['attr4_referent']['raw']
    assert '123-45-6789' == \
           decrypted_job_application_proof['requested_proof']['revealed_attrs']['attr5_referent']['raw']

    assert 'Alice' == decrypted_job_application_proof['requested_proof']['self_attested_attrs']['attr1_referent']
    assert 'Garcia' == decrypted_job_application_proof['requested_proof']['self_attested_attrs']['attr2_referent']
    assert '123-45-6789' == decrypted_job_application_proof['requested_proof']['self_attested_attrs']['attr6_referent']

    assert await anoncreds.verifier_verify_proof(job_application_proof_request_json,
                                                 decrypted_job_application_proof_json,
                                                 schemas_json, cred_defs_json, revoc_ref_defs_json, revoc_regs_json)

    logger.info("==============================")
    logger.info("4.3.0 == Apply for the job with Acme - Getting Job Certificate Credential ==")
    logger.info("------------------------------")

    logger.info("4.3.1 \"Acme\" -> Create \"Job Certificate\" Credential Offer for Alice")
    job_certificate_cred_offer_json = \
        await anoncreds.issuer_create_credential_offer(acme_wallet, acme_job_certificate_cred_def_id)

    logger.info("4.2.2 \"Acme\" -> Get key for Alice did")
    alice_acme_verkey = await did.key_for_did(pool_handle, acme_wallet, acme_alice_connection_response['did'])

    logger.info("4.3.3 \"Acme\" -> Authcrypt \"Job Certificate\" Credential Offer for Alice")
    authcrypted_job_certificate_cred_offer = await crypto.auth_crypt(acme_wallet, acme_alice_key, alice_acme_verkey,
                                                                     job_certificate_cred_offer_json.encode('utf-8'))

    logger.info("4.3.4 \"Acme\" -> Send authcrypted \"Job Certificate\" Credential Offer to Alice (simulated)")

    logger.info("4.3.5 \"Alice\" -> Authdecrypted \"Job Certificate\" Credential Offer from Acme")
    acme_alice_verkey, authdecrypted_job_certificate_cred_offer_json, authdecrypted_job_certificate_cred_offer = \
        await auth_decrypt(alice_wallet, alice_acme_key, authcrypted_job_certificate_cred_offer)

    logger.info("4.3.6 \"Alice\" -> Get \"Acme Job Certificate\" Credential Definition from Ledger")
    (_, acme_job_certificate_cred_def) = \
        await get_cred_def(pool_handle, alice_acme_did, authdecrypted_job_certificate_cred_offer['cred_def_id'])

    logger.info("4.3.7 \"Alice\" -> Create and store in Wallet \"Job Certificate\" Credential Request for Acme")
    (job_certificate_cred_request_json, job_certificate_cred_request_metadata_json) = \
        await anoncreds.prover_create_credential_req(alice_wallet, alice_acme_did,
                                                     authdecrypted_job_certificate_cred_offer_json,
                                                     acme_job_certificate_cred_def, alice_master_secret_id)

    logger.info("4.3.8 \"Alice\" -> Authcrypt \"Job Certificate\" Credential Request for Acme")
    authcrypted_job_certificate_cred_request_json = \
        await crypto.auth_crypt(alice_wallet, alice_acme_key, acme_alice_verkey,
                                job_certificate_cred_request_json.encode('utf-8'))

    logger.info("4.3.9 \"Alice\" -> Send authcrypted \"Job Certificate\" Credential Request to Acme (simulated)")

    logger.info("4.3.10 \"Acme\" -> Authdecrypt \"Job Certificate\" Credential Request from Alice")
    alice_acme_verkey, authdecrypted_job_certificate_cred_request_json, _ = \
        await auth_decrypt(acme_wallet, acme_alice_key, authcrypted_job_certificate_cred_request_json)

    logger.info("4.3.11 \"Acme\" -> Create \"Job Certificate\" Credential for Alice")
    alice_job_certificate_cred_values_json = json.dumps({
        "first_name": {"raw": "Alice", "encoded": "245712572474217942457235975012103335"},
        "last_name": {"raw": "Garcia", "encoded": "312643218496194691632153761283356127"},
        "employee_status": {"raw": "Permanent", "encoded": "2143135425425143112321314321"},
        "salary": {"raw": "2400", "encoded": "2400"},
        "experience": {"raw": "10", "encoded": "10"}
    })

    job_certificate_cred_json, _, _ = \
        await anoncreds.issuer_create_credential(acme_wallet, job_certificate_cred_offer_json,
                                                 authdecrypted_job_certificate_cred_request_json,
                                                 alice_job_certificate_cred_values_json, None, None)

    logger.info("4.3.12 \"Acme\" -> Authcrypt \"Job Certificate\" Credential for Alice")
    authcrypted_job_certificate_cred_json = \
        await crypto.auth_crypt(acme_wallet, acme_alice_key, alice_acme_verkey,
                                job_certificate_cred_json.encode('utf-8'))

    logger.info("4.3.13 \"Acme\" -> Send authcrypted \"Job Certificate\" Credential to Alice (simulated)")

    logger.info("4.3.14 \"Alice\" -> Authdecrypted \"Job Certificate\" Credential from Acme")
    _, authdecrypted_job_certificate_cred_json, _ = \
        await auth_decrypt(alice_wallet, alice_acme_key, authcrypted_job_certificate_cred_json)

    logger.info("4.3.15 \"Alice\" -> Store \"Job Certificate\" Credential")
    await anoncreds.prover_store_credential(alice_wallet, None, job_certificate_cred_request_metadata_json,
                                            authdecrypted_job_certificate_cred_json,
                                            acme_job_certificate_cred_def_json, None)

    logger.info("==============================")
    logger.info("5.1.0 === Apply for the loan with Thrift ==")
    logger.info("==============================")
    logger.info("5.1.0 == Apply for the loan with Thrift - Onboarding ==")
    logger.info("------------------------------")

    _, thrift_alice_key, alice_thrift_did, alice_thrift_key, \
    thrift_alice_connection_response = \
        await onboarding("5.1", pool_handle, "Thrift", thrift_wallet, thrift_did, 
                        "Alice", alice_wallet, alice_wallet_config, alice_wallet_credentials)

    logger.info("==============================")
    logger.info("5.2.0 == Apply for the loan with Thrift - Job Certificate proving  ==")
    logger.info("------------------------------")

    logger.info("5.2.1 \"Thrift\" -> Create \"Loan-Application-Basic\" Proof Request")
    apply_loan_proof_request_json = json.dumps({
        'nonce': '123432421212',
        'name': 'Loan-Application-Basic',
        'version': '0.1',
        'requested_attributes': {
            'attr1_referent': {
                'name': 'employee_status',
                'restrictions': [{'cred_def_id': acme_job_certificate_cred_def_id}]
            }
        },
        'requested_predicates': {
            'predicate1_referent': {
                'name': 'salary',
                'p_type': '>=',
                'p_value': 2000,
                'restrictions': [{'cred_def_id': acme_job_certificate_cred_def_id}]
            },
            'predicate2_referent': {
                'name': 'experience',
                'p_type': '>=',
                'p_value': 1,
                'restrictions': [{'cred_def_id': acme_job_certificate_cred_def_id}]
            }
        }
    })

    logger.info("5.2.2 \"Thrift\" -> Get key for Alice did")
    alice_thrift_verkey = await did.key_for_did(pool_handle, thrift_wallet, thrift_alice_connection_response['did'])

    logger.info("5.2.3 \"Thrift\" -> Authcrypt \"Loan-Application-Basic\" Proof Request for Alice")
    authcrypted_apply_loan_proof_request_json = \
        await crypto.auth_crypt(thrift_wallet, thrift_alice_key, alice_thrift_verkey,
                                apply_loan_proof_request_json.encode('utf-8'))

    logger.info("5.2.4 \"Thrift\" -> Send authcrypted \"Loan-Application-Basic\" Proof Request to Alice (simulated)")

    logger.info("5.2.5 \"Alice\" -> Authdecrypt \"Loan-Application-Basic\" Proof Request from Thrift")
    thrift_alice_verkey, authdecrypted_apply_loan_proof_request_json, _ = \
        await auth_decrypt(alice_wallet, alice_thrift_key, authcrypted_apply_loan_proof_request_json)

    logger.info("5.2.6 \"Alice\" -> Get credentials for \"Loan-Application-Basic\" Proof Request")

    search_for_apply_loan_proof_request = \
        await anoncreds.prover_search_credentials_for_proof_req(alice_wallet,
                                                                authdecrypted_apply_loan_proof_request_json, None)

    cred_for_attr1 = await get_credential_for_referent(search_for_apply_loan_proof_request, 'attr1_referent')
    cred_for_predicate1 = await get_credential_for_referent(search_for_apply_loan_proof_request, 'predicate1_referent')
    cred_for_predicate2 = await get_credential_for_referent(search_for_apply_loan_proof_request, 'predicate2_referent')

    await anoncreds.prover_close_credentials_search_for_proof_req(search_for_apply_loan_proof_request)

    creds_for_apply_loan_proof = {cred_for_attr1['referent']: cred_for_attr1,
                                  cred_for_predicate1['referent']: cred_for_predicate1,
                                  cred_for_predicate2['referent']: cred_for_predicate2}

    schemas_json, cred_defs_json, revoc_states_json = \
        await prover_get_entities_from_ledger("5.2", pool_handle, alice_thrift_did, creds_for_apply_loan_proof, 'Alice')

    logger.info("5.2.9 \"Alice\" -> Create \"Loan-Application-Basic\" Proof")
    apply_loan_requested_creds_json = json.dumps({
        'self_attested_attributes': {},
        'requested_attributes': {
            'attr1_referent': {'cred_id': cred_for_attr1['referent'], 'revealed': True}
        },
        'requested_predicates': {
            'predicate1_referent': {'cred_id': cred_for_predicate1['referent']},
            'predicate2_referent': {'cred_id': cred_for_predicate2['referent']}
        }
    })
    alice_apply_loan_proof_json = \
        await anoncreds.prover_create_proof(alice_wallet, authdecrypted_apply_loan_proof_request_json,
                                            apply_loan_requested_creds_json, alice_master_secret_id, schemas_json,
                                            cred_defs_json, revoc_states_json)

    logger.info("5.2.10 \"Alice\" -> Authcrypt \"Loan-Application-Basic\" Proof for Thrift")
    authcrypted_alice_apply_loan_proof_json = \
        await crypto.auth_crypt(alice_wallet, alice_thrift_key, thrift_alice_verkey,
                                alice_apply_loan_proof_json.encode('utf-8'))

    logger.info("5.2.11 \"Alice\" -> Send authcrypted \"Loan-Application-Basic\" Proof to Thrift (simulated)")

    logger.info("5.2.12 \"Thrift\" -> Authdecrypted \"Loan-Application-Basic\" Proof from Alice")
    _, authdecrypted_alice_apply_loan_proof_json, authdecrypted_alice_apply_loan_proof = \
        await auth_decrypt(thrift_wallet, thrift_alice_key, authcrypted_alice_apply_loan_proof_json)

    logger.info("5.2.13.1\"Thrift\" -> Get Schemas, Credential Definitions and Revocation Registries from Ledger required for Proof verifying")

    schemas_json, cred_defs_json, revoc_defs_json, revoc_regs_json = \
        await verifier_get_entities_from_ledger("5.2", pool_handle, thrift_did,
                                                authdecrypted_alice_apply_loan_proof['identifiers'], 'Thrift')

    logger.info("5.2.16 \"Thrift\" -> Verify \"Loan-Application-Basic\" Proof from Alice")
    assert 'Permanent' == \
           authdecrypted_alice_apply_loan_proof['requested_proof']['revealed_attrs']['attr1_referent']['raw']

    assert await anoncreds.verifier_verify_proof(apply_loan_proof_request_json,
                                                 authdecrypted_alice_apply_loan_proof_json,
                                                 schemas_json, cred_defs_json, revoc_defs_json, revoc_regs_json)

    logger.info("==============================")
    logger.info("5.3.0 == Apply for the loan with Thrift - Transcript and Job Certificate proving  ==")
    logger.info("------------------------------")

    logger.info("5.3.1 \"Thrift\" -> Create \"Loan-Application-KYC\" Proof Request")
    apply_loan_kyc_proof_request_json = json.dumps({
        'nonce': '123432421212',
        'name': 'Loan-Application-KYC',
        'version': '0.1',
        'requested_attributes': {
            'attr1_referent': {'name': 'first_name'},
            'attr2_referent': {'name': 'last_name'},
            'attr3_referent': {'name': 'ssn'}
        },
        'requested_predicates': {}
    })

    logger.info("5.2.2 \"Thrift\" -> Get key for Alice did")
    alice_thrift_verkey = await did.key_for_did(pool_handle, thrift_wallet, thrift_alice_connection_response['did'])

    logger.info("5.3.3 \"Thrift\" -> Authcrypt \"Loan-Application-KYC\" Proof Request for Alice")
    authcrypted_apply_loan_kyc_proof_request_json = \
        await crypto.auth_crypt(thrift_wallet, thrift_alice_key, alice_thrift_verkey,
                                apply_loan_kyc_proof_request_json.encode('utf-8'))

    logger.info("5.3.4 \"Thrift\" -> Send authcrypted \"Loan-Application-KYC\" Proof Request to Alice (simulated)")

    logger.info("5.3.5 \"Alice\" -> Authdecrypt \"Loan-Application-KYC\" Proof Request from Thrift")
    thrift_alice_verkey, authdecrypted_apply_loan_kyc_proof_request_json, _ = \
        await auth_decrypt(alice_wallet, alice_thrift_key, authcrypted_apply_loan_kyc_proof_request_json)

    logger.info("5.3.6 \"Alice\" -> Get credentials for \"Loan-Application-KYC\" Proof Request")

    search_for_apply_loan_kyc_proof_request = \
        await anoncreds.prover_search_credentials_for_proof_req(alice_wallet,
                                                                authdecrypted_apply_loan_kyc_proof_request_json, None)

    cred_for_attr1 = await get_credential_for_referent(search_for_apply_loan_kyc_proof_request, 'attr1_referent')
    cred_for_attr2 = await get_credential_for_referent(search_for_apply_loan_kyc_proof_request, 'attr2_referent')
    cred_for_attr3 = await get_credential_for_referent(search_for_apply_loan_kyc_proof_request, 'attr3_referent')

    await anoncreds.prover_close_credentials_search_for_proof_req(search_for_apply_loan_kyc_proof_request)

    creds_for_apply_loan_kyc_proof = {cred_for_attr1['referent']: cred_for_attr1,
                                      cred_for_attr2['referent']: cred_for_attr2,
                                      cred_for_attr3['referent']: cred_for_attr3}

    schemas_json, cred_defs_json, revoc_states_json = \
        await prover_get_entities_from_ledger("5.3", pool_handle, alice_thrift_did, creds_for_apply_loan_kyc_proof, 'Alice')

    logger.info("5.3.9 \"Alice\" -> Create \"Loan-Application-KYC\" Proof")

    apply_loan_kyc_requested_creds_json = json.dumps({
        'self_attested_attributes': {},
        'requested_attributes': {
            'attr1_referent': {'cred_id': cred_for_attr1['referent'], 'revealed': True},
            'attr2_referent': {'cred_id': cred_for_attr2['referent'], 'revealed': True},
            'attr3_referent': {'cred_id': cred_for_attr3['referent'], 'revealed': True}
        },
        'requested_predicates': {}
    })

    alice_apply_loan_kyc_proof_json = \
        await anoncreds.prover_create_proof(alice_wallet, authdecrypted_apply_loan_kyc_proof_request_json,
                                            apply_loan_kyc_requested_creds_json, alice_master_secret_id,
                                            schemas_json, cred_defs_json, revoc_states_json)

    logger.info("5.3.10 \"Alice\" -> Authcrypt \"Loan-Application-KYC\" Proof for Thrift")
    authcrypted_alice_apply_loan_kyc_proof_json = \
        await crypto.auth_crypt(alice_wallet, alice_thrift_key, thrift_alice_verkey,
                                alice_apply_loan_kyc_proof_json.encode('utf-8'))

    logger.info("5.3.11 \"Alice\" -> Send authcrypted \"Loan-Application-KYC\" Proof to Thrift (simulated)")

    logger.info("5.3.12 \"Thrift\" -> Authdecrypted \"Loan-Application-KYC\" Proof from Alice")
    _, authdecrypted_alice_apply_loan_kyc_proof_json, authdecrypted_alice_apply_loan_kyc_proof = \
        await auth_decrypt(thrift_wallet, thrift_alice_key, authcrypted_alice_apply_loan_kyc_proof_json)

    logger.info("5.3.13.1 \"Thrift\" -> Get Schemas, Credential Definitions and Revocation Registries from Ledger required for Proof verifying")

    schemas_json, cred_defs_json, revoc_defs_json, revoc_regs_json = \
        await verifier_get_entities_from_ledger("5.3", pool_handle, thrift_did,
                                                authdecrypted_alice_apply_loan_kyc_proof['identifiers'], 'Thrift')

    logger.info("5.3.16 \"Thrift\" -> Verify \"Loan-Application-KYC\" Proof from Alice")
    assert 'Alice' == \
           authdecrypted_alice_apply_loan_kyc_proof['requested_proof']['revealed_attrs']['attr1_referent']['raw']
    assert 'Garcia' == \
           authdecrypted_alice_apply_loan_kyc_proof['requested_proof']['revealed_attrs']['attr2_referent']['raw']
    assert '123-45-6789' == \
           authdecrypted_alice_apply_loan_kyc_proof['requested_proof']['revealed_attrs']['attr3_referent']['raw']

    assert await anoncreds.verifier_verify_proof(apply_loan_kyc_proof_request_json,
                                                 authdecrypted_alice_apply_loan_kyc_proof_json,
                                                 schemas_json, cred_defs_json, revoc_defs_json, revoc_regs_json)

    logger.info("==============================")

    logger.info("6.0.1 \"Sovrin Steward\" -> Close and Delete wallet")
    await wallet.close_wallet(steward_wallet)
    await wallet.delete_wallet(steward_wallet_config, steward_wallet_credentials)

    logger.info("6.0.2 \"Government\" -> Close and Delete wallet")
    await wallet.close_wallet(government_wallet)
    await wallet.delete_wallet(government_wallet_config, government_wallet_credentials)

    logger.info("6.0.3 \"Faber\" -> Close and Delete wallet")
    await wallet.close_wallet(faber_wallet)
    await wallet.delete_wallet(faber_wallet_config, faber_wallet_credentials)

    logger.info("6.0.4 \"Acme\" -> Close and Delete wallet")
    await wallet.close_wallet(acme_wallet)
    await wallet.delete_wallet(acme_wallet_config, acme_wallet_credentials)

    logger.info("6.0.5 \"Thrift\" -> Close and Delete wallet")
    await wallet.close_wallet(thrift_wallet)
    await wallet.delete_wallet(thrift_wallet_config, thrift_wallet_credentials)

    logger.info("6.0.6 \"Alice\" -> Close and Delete wallet")
    await wallet.close_wallet(alice_wallet)
    await wallet.delete_wallet(alice_wallet_config, alice_wallet_credentials)

    logger.info("6.0.7 Close and Delete pool")
    await pool.close_pool_ledger(pool_handle)
    await pool.delete_pool_ledger_config(pool_name)

    logger.info("6.0.0 Getting started -> done")


async def onboarding(info_prefix, pool_handle, _from, from_wallet, from_did, 
                    to, to_wallet: Optional[str], to_wallet_config: str, to_wallet_credentials: str):
    logger.info("{}.1 \"{}\" -> Create and store in Wallet \"{} {}\" DID (from to)".format(info_prefix, _from, _from, to))
    (from_to_did, from_to_key) = await did.create_and_store_my_did(from_wallet, "{}")
    print("Create and store DID from DID: " + from_did)
    #print("Create and store DID from wallet: " + from_wallet)
    print("Create and store DID from_to DID: " + from_to_did)

    logger.info("{}.2 \"{}\" -> Send Nym to Ledger for \"{} {}\" DID (from to)".format(info_prefix, _from, _from, to))
    await send_nym(pool_handle, from_wallet, from_did, from_to_did, from_to_key, None)

    logger.info("{}.3 \"{}\" -> Send connection request to {} with \"{} {}\" DID and Nonce (simulated)".format(info_prefix, _from, to, _from, to))
    connection_request = {
        'did': from_to_did,
        'nonce': 123456789
    }
    print("Connection request: " + json.dumps(connection_request))

    if not to_wallet:
        logger.info("{}.4 \"{}\" -> Create wallet".format(info_prefix, to))
        try:
            await wallet.create_wallet(to_wallet_config, to_wallet_credentials)
        except IndyError as ex:
            if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
                pass
        to_wallet = await wallet.open_wallet(to_wallet_config, to_wallet_credentials)
        #print("Create wallet to wallet: " + to_wallet)

    logger.info("{}.5 \"{}\" -> Create and store in Wallet \"{} {}\" DID (to from)".format(info_prefix, to, to, _from))
    (to_from_did, to_from_key) = await did.create_and_store_my_did(to_wallet, "{}")
    #print("Create and store DID to wallet: " + to_wallet)
    print("Create and store DID to_from DID: " + to_from_did)

    logger.info("{}.6 \"{}\" -> Get key for did from \"{}\" connection request".format(info_prefix, to, _from))
    from_to_verkey = await did.key_for_did(pool_handle, to_wallet, connection_request['did'])

    logger.info("{}.7 \"{}\" -> Anoncrypt connection response for \"{}\" with \"{} {}\" DID, Verkey and Nonce"
                .format(info_prefix, to, _from, to, _from))
    connection_response = json.dumps({
        'did': to_from_did,
        'verkey': to_from_key,
        'nonce': connection_request['nonce']
    })
    print("Connection response: " + connection_response)
    anoncrypted_connection_response = await crypto.anon_crypt(from_to_verkey, connection_response.encode('utf-8'))

    logger.info("{}.8 \"{}\" -> Send anoncrypted connection response to \"{}\" (simulated)".format(info_prefix, to, _from))

    logger.info("{}.9 \"{}\" -> Anondecrypt connection response from \"{}\"".format(info_prefix, _from, to))
    decrypted_connection_response = \
        json.loads((await crypto.anon_decrypt(from_wallet, from_to_key,
                                              anoncrypted_connection_response)).decode("utf-8"))
    print("Decrypted connection response: " + json.dumps(decrypted_connection_response))

    logger.info("{}.10 \"{}\" -> Authenticates \"{}\" by comparing Nonces".format(info_prefix, _from, to))
    assert connection_request['nonce'] == decrypted_connection_response['nonce']

    logger.info("{}.11 \"{}\" -> Send Nym to Ledger for \"{} {}\" DID (to from)".format(info_prefix, _from, to, _from))
    await send_nym(pool_handle, from_wallet, from_did, to_from_did, to_from_key, None)

    return to_wallet, from_to_key, to_from_did, to_from_key, decrypted_connection_response


async def get_verinym(info_prefix, pool_handle, _from, from_wallet, from_did, from_to_key,
                      to, to_wallet, to_from_did, to_from_key, role):
    logger.info("{}.12 \"{}\" -> Create and store in Wallet \"{}\" new DID".format(info_prefix, to, to))
    (to_did, to_key) = await did.create_and_store_my_did(to_wallet, "{}")
    print( "To DID: " + to_did)

    logger.info("{}.13 \"{}\" -> Authcrypt \"{} DID info\" for \"{}\"".format(info_prefix, to, to, _from))
    did_info_json = json.dumps({
        'did': to_did,
        'verkey': to_key
    })
    authcrypted_did_info_json = \
        await crypto.auth_crypt(to_wallet, to_from_key, from_to_key, did_info_json.encode('utf-8'))

    logger.info("{}.14 \"{}\" -> Send authcrypted \"{} DID info\" to {} (simulated)".format(info_prefix, to, to, _from))

    logger.info("{}.15 \"{}\" -> Authdecrypted \"{} DID info\" from {}".format(info_prefix, _from, to, to))
    sender_verkey, authdecrypted_did_info_json, authdecrypted_did_info = \
        await auth_decrypt(from_wallet, from_to_key, authcrypted_did_info_json)

    logger.info("{}.16 \"{}\" -> Authenticate {} by comparing Verkeys".format(info_prefix, _from, to, ))
    assert sender_verkey == await did.key_for_did(pool_handle, from_wallet, to_from_did)

    logger.info("{}.17 \"{}\" -> Send Nym to Ledger for \"{} DID\" with {} Role".format(info_prefix, _from, to, role))
    await send_nym(pool_handle, from_wallet, from_did, authdecrypted_did_info['did'],
                   authdecrypted_did_info['verkey'], role)

    return to_did


async def send_nym(pool_handle, wallet_handle, _did, new_did, new_key, role):
    nym_request = await ledger.build_nym_request(_did, new_did, new_key, None, role)
    print("SEND_NYM: " + nym_request)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, _did, nym_request)


async def send_schema(pool_handle, wallet_handle, _did, schema):
    schema_request = await ledger.build_schema_request(_did, schema)
    print("SEND_SCHEMA: " + schema_request)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, _did, schema_request)


async def send_cred_def(pool_handle, wallet_handle, _did, cred_def_json):
    cred_def_request = await ledger.build_cred_def_request(_did, cred_def_json)
    print("SEND_CRED_DEF: " + cred_def_request)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, _did, cred_def_request)


async def get_schema(pool_handle, _did, schema_id):
    get_schema_request = await ledger.build_get_schema_request(_did, schema_id)
    print("GET_SCHEMA: " + get_schema_request)
    get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
    print("GET_SCHEMA: " + get_schema_response)
    return await ledger.parse_get_schema_response(get_schema_response)


async def get_cred_def(pool_handle, _did, schema_id):
    get_cred_def_request = await ledger.build_get_cred_def_request(_did, schema_id)
    print("GET_CRED_DEF: " + get_cred_def_request)
    get_cred_def_response = await ledger.submit_request(pool_handle, get_cred_def_request)
    print("GET_CRED_DEF: " + get_cred_def_response)
    return await ledger.parse_get_cred_def_response(get_cred_def_response)


async def get_credential_for_referent(search_handle, referent):
    credentials = json.loads(
        await anoncreds.prover_fetch_credentials_for_proof_req(search_handle, referent, 10))
    print("GET_CRED_REFERENT: " + json.dumps(credentials[0]))
    return credentials[0]['cred_info']


async def prover_get_entities_from_ledger(info_prefix, pool_handle, _did, identifiers, actor):
    schemas = {}
    cred_defs = {}
    rev_states = {}
    for item in identifiers.values():
        logger.info("{}.7 \"{}\" -> Get Schema from Ledger".format(info_prefix, actor))
        (received_schema_id, received_schema) = await get_schema(pool_handle, _did, item['schema_id'])
        schemas[received_schema_id] = json.loads(received_schema)

        logger.info("{}.8 \"{}\" -> Get Claim Definition from Ledger".format(info_prefix, actor))
        (received_cred_def_id, received_cred_def) = await get_cred_def(pool_handle, _did, item['cred_def_id'])
        cred_defs[received_cred_def_id] = json.loads(received_cred_def)

        if 'rev_reg_seq_no' in item:
            pass  # TODO Create Revocation States

    return json.dumps(schemas), json.dumps(cred_defs), json.dumps(rev_states)


async def verifier_get_entities_from_ledger(info_prefix, pool_handle, _did, identifiers, actor):
    schemas = {}
    cred_defs = {}
    rev_reg_defs = {}
    rev_regs = {}
    for item in identifiers:
        logger.info("{}.14 \"{}\" -> Get Schema from Ledger".format(info_prefix, actor))
        (received_schema_id, received_schema) = await get_schema(pool_handle, _did, item['schema_id'])
        schemas[received_schema_id] = json.loads(received_schema)

        logger.info("{}.15 \"{}\" -> Get Claim Definition from Ledger".format(info_prefix, actor))
        (received_cred_def_id, received_cred_def) = await get_cred_def(pool_handle, _did, item['cred_def_id'])
        cred_defs[received_cred_def_id] = json.loads(received_cred_def)

        if 'rev_reg_seq_no' in item:
            pass  # TODO Get Revocation Definitions and Revocation Registries

    return json.dumps(schemas), json.dumps(cred_defs), json.dumps(rev_reg_defs), json.dumps(rev_regs)


async def auth_decrypt(wallet_handle, key, message):
    from_verkey, decrypted_message_json = await crypto.auth_decrypt(wallet_handle, key, message)
    decrypted_message_json = decrypted_message_json.decode("utf-8")
    decrypted_message = json.loads(decrypted_message_json)
    return from_verkey, decrypted_message_json, decrypted_message


if __name__ == '__main__':
    run_coroutine(run)
    time.sleep(1)  # FIXME waiting for libindy thread complete