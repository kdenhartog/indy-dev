#!/bin/bash

#Stop and remove all running Indy containers
echo "Remove all of these following images and your .indy_client?"
  docker ps -a | grep '\indy_dev_pool\|indy_dev' # | '{print $1}'
read -p "Yes or no" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  docker ps -a | awk '{ print $1,$2}' | grep indy_dev | xargs docker rm
  docker rmi $(docker images -a | grep '\indy_dev_pool\|indy_dev' | awk '{print $1}') -f
  rm -rf .indy_client
fi
