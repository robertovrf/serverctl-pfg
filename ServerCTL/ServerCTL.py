from flask import Flask, jsonify,request
from os import path
import yaml, time, os
from kubernetes import client, config, utils
from kubernetes.client.api import core_v1_api


#### Kubernetes Functions ####
def deploymentName(DeploymentName):

    deploy = ["apiVersion: apps/v1\n","kind: Deployment\n","metadata:\n","  name: ",DeploymentName,"\n","  labels:\n","    app: ",DeploymentName,"\n","spec:\n",
    "  replicas: 1\n","  selector:\n","    matchLabels:\n","      app: ",DeploymentName,"\n","  template:\n","    metadata:\n","      labels:\n","        app: ",DeploymentName,"\n",
    "    spec:\n","      containers:\n","      - name: ",DeploymentName,"\n","        image: docker.io/rsdias/distributor:remote\n","        imagePullPolicy: Always\n",
    "        ports:\n","        - containerPort: 5000\n","        - containerPort: 5001\n",
    ]
    service = ["apiVersion: v1\n","kind: Service\n","metadata:\n","  name: ",DeploymentName,"\n","spec:\n","  ports:\n","  - port: 5000\n","    name: tcp1\n",
    "    targetPort: 5000\n","  - port : 5001\n","    name: tcp2\n","    targetPort: 5001\n","  selector:\n","    app: ",DeploymentName,"\n","  type: ClusterIP\n"
    ]
    file1 = open('%s.yaml' %(DeploymentName), "x")
    file1.writelines(deploy)
    file1.close()
    file2 = open('%s-service.yaml' %(DeploymentName), "x")
    file2.writelines(service)
    file2.close()

def podName(DeployName):
    #config.load_kube_config()
    #config.load_incluster_config()
    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        if ( i.metadata.name.startswith(DeployName)):
             return i.metadata.name

def create_service(Deployname):
    core_v1_api = client.CoreV1Api()
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name="%s-service" % Deployname
        ),
        spec=client.V1ServiceSpec(
            selector={"app": Deployname},
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

def getClusterIP(Deployname):
    core_v1_api = client.CoreV1Api()
    service = core_v1_api.read_namespaced_service(name="%s-service" % Deployname, namespace="default")
    return service.spec.cluster_ip

def verifyStatus(pod_name):
    core_v1 = core_v1_api.CoreV1Api()
    api_response = core_v1.read_namespaced_pod(name=pod_name,namespace="default")
    return api_response.status.phase

def createDeployment(name):
    deploymentName(name)
    api_instance = core_v1_api.CoreV1Api()
    with open(path.join(path.dirname(__file__),'%s.yaml' %name)) as f:
            dep = yaml.safe_load(f)
            k8s_apps_v1 = client.AppsV1Api()
            resp = k8s_apps_v1.create_namespaced_deployment(body=dep,namespace="default")
            print("Deployment created. Deployment Name = '%s'" % resp.metadata.name)
    os.remove('%s.yaml' %name)
    k8sClient = client.ApiClient()
    utils.create_from_yaml(k8sClient, "%s-service.yaml" %name)
    os.remove('%s-service.yaml' %name)


app = Flask(__name__)
names = [
    {
        'id': 1,
        'name': u'serverctl-service',
        'creator' : u'serverctl'
    }
]
inicio = 0
total = 0
deployquantity = 0
@app.route('/names/many', methods=['GET'])
def get_names():
    #return jsonify({'names': names})
    return str(deployquantity)

@app.route('/names/final', methods=['GET'])
def get_amount():
    return str(total)

@app.route('/names', methods=['POST'])
def createService():
    if not request.json or not 'name' in request.json:
        abort(400)
    name = {
        'id': names[-1]['id'] + 1,
        'name': request.json['name'],
    }
    names.append(name)
    servicename = request.json['name']
    finalname = servicename.lower()
    createDeployment(finalname)
    return jsonify({'name': name}), 201

@app.route('/names/many' , methods=['POST'])
def createPods():
    if not request.json or not 'name' in request.json:
        abort(400)

    quantity = request.json['quantity']
    name = request.json['name']
    global inicio
    global total
    global deployquantity
    for x in range(inicio+1,inicio+quantity+1):
        deployname = name+str(x)
        finalname = deployname.lower()
        createDeployment(finalname)
        #print(finalname)
        newname = {
        'id': names[-1]['id'] + 1,
        'name': finalname,
        'creator' : 'distributor'
        }
        names.append(newname)
        total = total + 1
    inicio = inicio + quantity
    deployquantity = quantity
    return jsonify({'name' : name}),201


if __name__ == '__main__':
    #config.load_kube_config() # to work localy
    config.load_incluster_config() # to work inside the cluster
    app.run(host="0.0.0.0",port=5000)
