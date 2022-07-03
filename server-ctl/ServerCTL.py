from flask import Flask, jsonify,request
import yaml, time
from kubernetes import client, config, utils
from kubernetes.client.api import core_v1_api

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
            image: docker.io/rsdias/distributor:remote
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
        type: CluseterIP
  ''')
  
def create_deployment(name):
  deployment = load_deployment(name)
  api_instance = core_v1_api.CoreV1Api()
  k8s_apps_v1 = client.AppsV1Api()
  resp = k8s_apps_v1.create_namespaced_deployment(body=deployment,namespace="default")

  service = load_service(name)
  k8s_client = client.ApiClient()
  utils.create_from_yaml(k8s_client, service)

def create_service(deployment_name):
  core_v1_api = client.CoreV1Api()
  body = client.V1Service(
    api_version="v1",
    kind="Service",
    metadata=client.V1ObjectMeta(name="%s-service" % deployment_name),
    spec=client.V1ServiceSpec(
      selector={"app": deployment_name},
      ports=[client.V1ServicePort(
        name='tcp1',
        port=5000,
        target_port=5000),

      client.V1ServicePort(
        name='tcp2',
        port=5001,
        target_port=5001
      )]
    )
  )
  #Creation of the deployment on namespace default
  core_v1_api.create_namespaced_service(namespace="default", body=body)

# def get_cluster_ip(deployment_name):
#   core_v1_api = client.CoreV1Api()
#   service = core_v1_api.read_namespaced_service(name="%s-service" % deployment_name, namespace="default")
#   return service.spec.cluster_ip

# def verify_status(pod_name):
#   core_v1 = core_v1_api.CoreV1Api()
#   api_response = core_v1.read_namespaced_pod(name=pod_name,namespace="default")
#   return api_response.status.phase

### ENDPOINTS

@app.route('/pods', methods=['GET'])
def get_names():
  return jsonify(names)

@app.route('/pods/quantity', methods=['GET'])
def get_amount():
  return str(number_of_pods)

@app.route('/pods/service', methods=['POST'])
def create_service():
  if not request.json or not 'name' in request.json:
    abort(400)

  serviceName = request.json['name'].lower()

  names.append({
    'id': names[-1]['id'] + 1,
    'name': request.json['name'],
  })

  create_deployment(serviceName)

  return jsonify({'name': names[-1]}), 201

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
