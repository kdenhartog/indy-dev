#!/bin/bash
if docker --version > /dev/null
    then echo "Docker is installed. Double check that it's running before continuing."
    else echo "Docker isn't installed."
fi

if make --version > /dev/null
    then echo "make is installed."
    else echo "make isn't installed."
fi