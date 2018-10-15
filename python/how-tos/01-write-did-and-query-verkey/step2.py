        # Tell SDK which pool you are going to use and open it. You should have already started
        # this pool using docker compose or similar. Here, we are dumping the config
        # just for demonstration purposes. The pool_genesis_txn_path is a json file that lists 
        # information to find the nodes within the pool. This one has been configured to the pool
        # we built and is running through docker. The try-except clause is there to easily rerun,
        # this file. The IndySDK is designed to throw an error if you create a pool_genesis_txn_file
        # with the same name. This accounts for that to protect the developer for good dev usability.

        pool_config = json.dumps({'genesis_txn': str(pool_genesis_txn_path)})
        print_log('\n1. Create new pool ledger configuration to connect to ledger.\n')
        try:
            await pool.create_pool_ledger_config(pool_name, pool_config)
        except IndyError as ex:
            if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
                pass

        print_log('\n2. Open ledger and get handle\n')
        pool_handle = await pool.open_pool_ledger(config_name=pool_name, config=None)


        # Creates a wallet using a generic config. Be sure to check the IndySDK python wrapper for
        # detailed documentation of the different variations this wallet config can look like.
        # Additionally, we're setting credentials which is how we password protect and encrypt our
        # wallet. In this case, our password is "wallet_key" as defined in the template. In production,
        # the user should define this and it should have some sort of complexity validation to provide
        # proper protection of the wallet. DO NOT HARDCODE THIS IN PRODUCTION. Once we've created the
        # wallet we're now going to open it which allows us to interact with it by passing the
        # wallet_handle around.

        print_log('\n3. Create new identity wallet\n')
        await wallet.create_wallet(wallet_config, wallet_credentials)

        print_log('\n4. Open identity wallet and get handle\n')
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
