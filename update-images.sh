#!/bin/bash
./compile-dana.sh

docker build . -t gcr.io/pfg2022/remote-dist -f app/Dockerfile
docker build . -t gcr.io/pfg2022/server-ctl -f server-ctl/Dockerfile

docker push gcr.io/pfg2022/server-ctl:latest 
docker push gcr.io/pfg2022/remote-dist:latest 