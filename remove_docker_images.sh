#!/bin/bash
docker rmi server-ctl:latest
docker rmi robertovrf/server-ctl:latest
docker rmi remote-dist:latest
docker rmi robertovrf/remote-dist:latest
docker rmi distributor:latest
docker rmi python:3
docker rmi ubuntu:18.10
