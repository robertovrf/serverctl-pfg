from flask import Flask, jsonify,request
import yaml, time
from kubernetes import client, config

app = Flask(__name__)

names = [
  {
    'id': 1,
    'name': u'serverctl-service',
    'creator' : u'serverctl'
  }
]

last_pod_index = 0
number_of_pods = 0

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
            image: gcr.io/pfg2022/remote-dist
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
  
def create_deployment(name):
  deployment = load_deployment(name)
  k8s_apps_v1 = client.AppsV1Api()
  k8s_apps_v1.create_namespaced_deployment(body=deployment,namespace="default")

  try:
    service = load_service(name)
    k8s_client = client.CoreV1Api()
    k8s_client.create_namespaced_service(body=service, namespace="default")
  except:
    print("Service already created")
  

### ENDPOINTS

@app.route('/pods', methods=['GET'])
def get_names():
  return jsonify(names)

@app.route('/pods/quantity', methods=['GET'])
def get_amount():
  return str(number_of_pods)

@app.route('/pods/new', methods=['POST'])
def createPods():
  if not request.json or not 'name' in request.json:
    abort(400)

  global last_pod_index
  global number_of_pods
  quantity = request.json['quantity']
  name = request.json['name']

  for x in range(0, quantity):
    last_pod_index += 1
    deployment_name = (name + str(last_pod_index)).lower()
    create_deployment(deployment_name)
    names.append({
      'id': names[-1]['id'] + 1,
      'name': deployment_name,
      'creator' : 'distributor'
    })
  number_of_pods += quantity
  return jsonify({'name' : names[-1]}), 201

if __name__ == '__main__':
  #config.load_kube_config() # to work localy
  config.load_incluster_config() # to work inside the cluster
  app.run(host="0.0.0.0",port=5000)
