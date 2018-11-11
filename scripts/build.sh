#!/bin/bash

docker build -f indy-pool.dockerfile -t indy_dev_pool .
echo "Finished building indy_pool image"
docker build -f indy-dev.dockerfile -t indy_dev .
echo "Finished building indy_dev image"
