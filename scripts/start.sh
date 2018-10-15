#!/bin/bash

#Stop and remove all running Indy containers
docker run -itd --net=host -p 127.0.0.1:9701-9708:9701-9708 indy_pool
echo "Indy_pool running"
echo "You are now in the indy_dev environment command line"
docker run -it --net=host -p 127.0.0.1:8080:8080 -v $(pwd):/home/indy indy_dev
