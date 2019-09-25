mkdir c:\INDY
c:
cd c:\INDY
rm indy-dev -r -f
git clone https://github.com/kdenhartog/indy-dev.git
rem git clone https://github.com/mwherman2000/indy-dev.git
echo Press Enter to continue
pause

cd indy-dev
docker build -f indy-pool.dockerfile -t indy_pool .
docker build -f indy-dev.dockerfile -t indy_dev .
docker images
echo Press Enter to continue
pause