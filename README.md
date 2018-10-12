## Descriptions
This is an easy to configure development environment to play around with Hyperledger Indy. Files can be written in an IDE or text editor like VSCode on the host machine, while being able to have a consistent docker environment to run files in a simple way. It uses docker and docker images that are pre-configured to setup a pool (indy_pool) and a Indy development environment (indy_dev) and allow the devlopment environment to interact with the pool of indy_nodes. This is not intended to allow for indy-plenum, plenum-plugin, or  indy-node development. If you'd like to do that, check out sovrin's [token-plugin](https://github.com/sovrin-foundation/token-plugin#org003878b) repository.

## How to setup
1. [Download docker](https://docs.docker.com/install/#supported-platforms)
2. start docker
3. docker build -f indy-pool.dockerfile -t indy_pool .
4. docker build -f indy-dev.dockerfile -t indy_dev .

## How to start (OS X and Linux)
1. docker run -itd --net=host -p 127.0.0.1:9701-9708:9701-9708 indy_pool
2. docker run -it --net=host -p 127.0.0.1:8080:8080 -v $(pwd):/home/indy indy_dev

## How to start (Windows)
1. docker run -itd --net=host -p 127.0.0.1:9701-9708:9701-9708 indy_pool
2. docker run -it --net=host -p 127.0.0.1:8080:8080 -v %cd%:/home/indy indy_dev

## Test Python environment
Once inside the docker shell (started in step 2 of "how to start"):

1. cd python
2. python3 getting_started.py

If the getting started guide completes through the end of cleanup everything is working correctly.

## Going through the IndySDK How-to guides


## improvement plans
* Create Makefile
* Add Node.js wrapper support