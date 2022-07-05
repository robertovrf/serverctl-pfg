#!/bin/bash
./compile-dana.sh

docker build . -t robertovrf/distributor:latest -f app/distributor.Dockerfile
docker build . -t robertovrf/remote-dist:latest -f app/remotedist.Dockerfile
docker build . -t robertovrf/server-ctl:latest -f server-ctl/Dockerfile

docker push robertovrf/server-ctl:latest 
docker push robertovrf/distributor:latest 
docker push robertovrf/remote-dist:latest 