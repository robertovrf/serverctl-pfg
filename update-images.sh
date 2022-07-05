#!/bin/bash
./compile-dana.sh

docker build -t distributor:latest -f- . < distributor.Dockerfile
docker build -t remote-dist:latest -f- . < remotedist.Dockerfile
docker build -t server-ctl:latest -f- . < serverCTL.Dockerfile

docker tag distributor:lastest robertovrf/distributor:lastest
docker tag remote-dist:latest robertovrf/remote-dist:latest
docker tag server-ctl:latest robertovrf/server-ctl:latest

docker push robertovrf/server-ctl:latest 
docker push robertovrf/distributor:latest 
docker push robertovrf/remote-dist:latest 