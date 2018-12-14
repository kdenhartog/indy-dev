                # 20.
                print_log('\n20.Verifier is verifying proof from Prover\n')
                assert await anoncreds.verifier_verify_proof(proof_req_json, proof_json, json.dumps(schemas_json), json.dumps(cred_defs_json), revoc_regs_json, "{}")

                # 21
                print_log('\n21. Closing both wallet_handles\n')
                await wallet.close_wallet(steward_wallet_handle)
                await wallet.close_wallet(trust_anchor_wallet_handle)
                await wallet.close_wallet(prover_wallet_handle)

                # 22
                print_log('\n22. Deleting created wallet_handles\n')
                await wallet.delete_wallet(steward_wallet_config, wallet_credentials)
                await wallet.delete_wallet(trust_anchor_wallet_config, wallet_credentials)
                await wallet.delete_wallet(prover_wallet_config, prover_wallet_credentials)
