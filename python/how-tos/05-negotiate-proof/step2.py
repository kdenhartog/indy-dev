        # 1.
        print_log('\n1. Creates a new local pool ledger configuration that is used '
                  'later when connecting to ledger.\n')
        await pool.create_pool_ledger_config(pool_name, pool_config)

        # 2.
        print_log('\n2. Open pool ledger and get handle from libindy\n')
        pool_handle = await pool.open_pool_ledger(pool_name, None)

        # 3.
        print_log('\n3. Creating new issuer, steward, and prover secure wallet\n')
        await wallet.create_wallet(trust_anchor_wallet_config, wallet_credentials)
        await wallet.create_wallet(steward_wallet_config, wallet_credentials)

        # 4.
        print_log('\n4. Open wallet and get handle from libindy\n')
        trust_anchor_wallet_handle = await wallet.open_wallet(trust_anchor_wallet_config, wallet_credentials)
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
        trust_anchor_did, trust_anchor_verkey = await did.create_and_store_my_did(trust_anchor_wallet_handle, "{}")
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
        await ledger.sign_and_submit_request(pool_handle, trust_anchor_wallet_handle, trust_anchor_did, schema_request)
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

        (cred_def_id, cred_def_json) = await anoncreds.issuer_create_and_store_credential_def(trust_anchor_wallet_handle, trust_anchor_did, gvt_schema_json, cred_def_tag, cred_def_type, cred_def_config)
        cred_def_request = await ledger.build_cred_def_request(trust_anchor_did, cred_def_json)
        await ledger.sign_and_submit_request(pool_handle, trust_anchor_wallet_handle, trust_anchor_did, cred_def_request)
        
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
        cred_offer_json = await anoncreds.issuer_create_credential_offer(trust_anchor_wallet_handle, cred_def_id)
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
        (cred_json, _, _) = await anoncreds.issuer_create_credential(trust_anchor_wallet_handle, cred_offer_json, cred_req_json, cred_values_json, None, None)
        print_log('Credential: ')
        pprint.pprint(json.loads(cred_json))

        # 17.
        print_log('\n17. Prover processes and stores Credential\n')
        await anoncreds.prover_store_credential(prover_wallet_handle, None, cred_req_metadata_json, cred_json, cred_def_json, None)