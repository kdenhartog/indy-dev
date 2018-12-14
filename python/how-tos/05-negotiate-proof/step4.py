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

        cred_defs_json = {}
        get_cred_def_request = await ledger.build_get_cred_def_request(prover_did, cred_def_id)
        get_cred_def_response = await ledger.submit_request(pool_handle, get_cred_def_request)
        (received_cred_def_id, received_cred_def) = await ledger.parse_get_cred_def_response(get_cred_def_response)
        cred_defs_json[received_cred_def_id] = json.loads(received_cred_def)

        revoc_regs_json = json.dumps({})

        proof_json = await anoncreds.prover_create_proof(prover_wallet_handle, proof_req_json, requested_credentials_json, master_secret_id, json.dumps(schemas_json), json.dumps(cred_defs_json), revoc_regs_json)
        proof = json.loads(proof_json)

        assert 'Alex' == proof['requested_proof']['revealed_attrs']['attr1_referent'][1]
