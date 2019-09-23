docker run -itd --net=host -p 127.0.0.1:9701-9708:9701-9708 indy_pool
docker run -it --net=host -p 127.0.0.1:8080:8080 -v C:/INDY/indy-dev:/indy-dev indy_dev
echo Press Enter to continue
pause