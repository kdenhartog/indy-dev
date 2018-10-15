#!/bin/bash

#Stop and remove all running Indy containers
docker rmi $(docker images -a | grep indy | awk '{print $1}')