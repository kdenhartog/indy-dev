        # Tell SDK which pool you are going to use and open it. You should have already started
        # this pool using docker compose or similar. Here, we are dumping the config
        # just for demonstration purposes. The pool_genesis_txn_path is a json file that lists 
        # information to find the nodes within the pool. This one has been configured to the pool
        # we built and is running through docker. The try-except clause is there to easily rerun,
        # this file. The IndySDK is designed to throw an error if you create a pool_genesis_txn_file
        # with the same name. This accounts for that to protect the developer for good dev usability.

        # 1.
        print_log('\n1. Creates a new local pool ledger configuration that is used '
                'later when connecting to ledger.\n')
        await pool.create_pool_ledger_config(pool_name, pool_config)

        # 2.
        print_log('\n2. Open pool ledger and get handle from libindy\n')
        pool_handle = await pool.open_pool_ledger(pool_name, None)


        # Creates a wallet using a generic config. Be sure to check the IndySDK python wrapper for
        # detailed documentation of the different variations this wallet config can look like.
        # Additionally, we're setting credentials which is how we password protect and encrypt our
        # wallet. In this case, our password is "wallet_key" as defined in the template. In production,
        # the user should define this and it should have some sort of complexity validation to provide
        # proper protection of the wallet. DO NOT HARDCODE THIS IN PRODUCTION. Once we've created the
        # wallet we're now going to open it which allows us to interact with it by passing the
        # wallet_handle around.
       
        # 3.
        print_log('\n3. Creating new secure wallet\n')
        await wallet.create_wallet(wallet_name, wallet_credentials)

        # 4.
        print_log('\n4. Open wallet and get handle from libindy\n')
        wallet_handle = await wallet.open_wallet(wallet_name, wallet_credentials)
