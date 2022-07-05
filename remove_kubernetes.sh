#!/bin/bash
kubectl delete deploy distributor serverctl
kubectl delete svc distributor-service serverctl distributor