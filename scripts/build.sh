#!/bin/bash

docker build -f ./scripts/indy-pool.dockerfile -t indy_pool .
echo "Finished building indy_pool image"
docker build -f ./scripts/indy-dev.dockerfile -t indy_dev .
echo "Finished building indy_dev image"