docker stop $(docker ps -a | grep indy | awk '{print $1}')
docker rm $(docker ps -a | grep indy | awk '{print $1}')