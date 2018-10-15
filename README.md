## Descriptions
This is an easy to configure development environment to play around with Hyperledger Indy. Files can be written in an IDE or text editor like VSCode on the host machine, while being able to have a consistent docker environment to run files in a simple way. It uses docker and docker images that are pre-configured to setup a pool (indy_pool) and a Indy development environment (indy_dev) and allow the devlopment environment to interact with the pool of indy_nodes. This is not intended to allow for indy-plenum, plenum-plugin, or  indy-node development. If you'd like to do that, check out sovrin's [token-plugin](https://github.com/sovrin-foundation/token-plugin#org003878b) repository.

## Prerequisites
1. [Docker](https://docs.docker.com/install/#supported-platforms)
2. Make for [Mac](https://stackoverflow.com/questions/10265742/how-to-install-make-and-gcc-on-a-mac#10265766) or [Debian Linux](https://stackoverflow.com/questions/11934997/how-to-install-make-in-ubuntu#11935185)


## Using with Unix systems (OS X and Linux)

to build the indy_pool and indy_dev images run: `make build`

to start up the pool and the dev environment in the current working directory run: `make start`

to stop the docker containers, first exit the indy_dev container with `exit` and then run: `make stop`

to cleanup the docker images built run: `make cleanup`

## Windows
Your milage may vary on Windows and will be tougher to work with, continue at your own risk.

```
docker build -f indy-pool.dockerfile -t indy_pool .
docker build -f indy-dev.dockerfile -t indy_dev .
docker run -itd --net=host -p 127.0.0.1:9701-9708:9701-9708 indy_pool
docker run -it --net=host -p 127.0.0.1:8080:8080 -v %cd%:/home/indy indy_dev
```

## Test Python environment
Once inside the docker shell (started in step 2 of "how to start"):

```
cd python
python3 getting_started.py
```

If the getting started guide completes through the end of cleanup everything is working correctly.

## Going through the IndySDK How-to guides

Details to be added shortly

## improvement plans
* Fix Python How-to guides
* Finish DID-Auth example
* Add support for different versions of SDKs
* Add Node.js wrapper support (help wanted)
* Add Java wrapper support (help wanted)
* Add .net wrapper support (help wanted)
* Add Objective C wrapper support (help wanted)

## Makefile issues?
```
cd scripts
chmod +x *.sh
```

