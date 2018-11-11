#!/bin/bash
echo "Stopping these following images?"
    docker ps -a | grep '\indy_pool\|indy_dev' # | '{print $1}'
read -p "Are you sure? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker stop $(docker ps -a | grep '\indy_pool\|indy_dev' | awk '{print $1}')
fi
