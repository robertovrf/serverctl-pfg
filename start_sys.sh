kubectl apply -f distributor.yaml
kubectl apply -f serverctl.yaml
kubectl expose deployment distributor --type LoadBalancer --port 5000 --target-port 5000