#!/bin/bash

#Stop and remove all running Indy containers
if [ "$(docker ps -a -f status=running | grep indy_pool)" ]
    then
        docker run -it --net=host -p 127.0.0.1:8080:8080 -v $(pwd):/home/indy indy_dev
    else
        docker run -itd --net=host -p 127.0.0.1:9701-9708:9701-9708 indy_pool
        docker run -it --net=host -p 127.0.0.1:8080:8080 -v $(pwd):/home/indy indy_dev
fi
