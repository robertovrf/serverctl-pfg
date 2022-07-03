#!/bin/bash
docker build . -t remote-dist:all -f app/Dockerfile
docker build . -t server-ctl:all -f server-ctl/Dockerfile