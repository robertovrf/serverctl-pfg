from flask import Flask, jsonify,request
import yaml, time
from kubernetes import client, config

app = Flask(__name__)

names = []

#### Kubernetes Functions ####
def load_deployment(deployment_name):
  return yaml.safe_load(f'''
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: {deployment_name}
      labels:
        app: {deployment_name}
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: {deployment_name}
      template:
        metadata:
          labels:
            app: {deployment_name}
        spec:
          containers:
          - name: {deployment_name}
            image: robertovrf/remote-dist:latest
            imagePullPolicy: Always
            ports:
            - containerPort: 5000
            - containerPort: 5001
  ''')

def load_service(deployment_name):
  return yaml.safe_load(f'''
    apiVersion: v1
    kind: Service
    metadata:
      name: {deployment_name}
    spec:
      ports:
      - port: 5000
        name: tcp1
        targetPort: 5000
      - port: 5001
        name: tcp2
        targetPort: 5001
      selector:
        app: {deployment_name}
      type: ClusterIP
  ''')
  
def create_component(name):
  # Create deployment
  deployment = load_deployment(name)
  k8s_apps_v1 = client.AppsV1Api()
  k8s_apps_v1.create_namespaced_deployment(body=deployment,namespace="default")

  # Create service
  try:
    service = load_service(name)
    k8s_client = client.CoreV1Api()
    k8s_client.create_namespaced_service(body=service, namespace="default")
  except:
    print("Service already created")

def delete_component(name):
  # Delete deployment
  k8s_apps_v1 = client.AppsV1Api()
  api_response = k8s_apps_v1.delete_namespaced_deployment(name=name, namespace="default")
  print(api_response)

# Delete service
  k8s_client = client.CoreV1Api()
  k8s_client.delete_namespaced_service(name=name, namespace="default")


### ENDPOINTS

@app.route('/pods', methods=['GET'])
def get_names():
  return jsonify(names)

@app.route('/pods/quantity', methods=['GET'])
def get_amount():
  return str(len(names))

@app.route('/pods/new', methods=['POST'])
def createPods():
  if not request.json or not 'name' in request.json:
    abort(400)

  quantity = request.json['quantity']
  name = request.json['name']

  global names

  for pod_index in range(0, quantity):
    deployment_name = (name + str(pod_index)).lower()
    create_component(deployment_name)
    names.append(deployment_name)
  return jsonify(names), 201


@app.route('/pods/delete', methods=['POST'])
def deletePods():
  
  global names

  for name in names:
    delete_component(name)
  
  names.clear()
  return jsonify(names), 201

if __name__ == '__main__':
  #config.load_kube_config() # to work localy
  config.load_incluster_config() # to work inside the cluster
  app.run(host="0.0.0.0",port=5000)
