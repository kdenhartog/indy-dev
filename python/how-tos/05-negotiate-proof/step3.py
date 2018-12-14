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
        'restrictions': [{'issuer_did': trust_anchor_did}]
        print_log('Proof Request: ')
        pprint.pprint(proof_request)
        proof_req_json = json.dumps(proof_request)
        claims_for_proof_request_json = await anoncreds.prover_get_credentials_for_proof_req(prover_wallet_handle,
                                                                                            proof_req_json)
        claims_for_proof_request = json.loads(claims_for_proof_request_json)
        print_log('Claims for Proof Request: ')
        pprint.pprint(claims_for_proof_request)
