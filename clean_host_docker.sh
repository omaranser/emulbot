docker container stop $(docker container ls -a -q)
docker network rm nw_local nw_internet
docker container prune -f 
