from flask import Flask, request
from flask_cors import CORS
import json
from Client import ClientSockClass, controller, utils, requests


app = Flask(__name__)

CORS(app)

@app.route("/", methods=['GET'])
def home():
    return {'msg':'a api esta no ar'}

@app.route('/createaccount', methods=["GET"])
def  create_account():
    args = request.args

    ip = args.get('ip', type=str)
    email = args.get('email',  type=str)

    client = ClientSockClass.ClientSocket(ip=ip)

    (status, resp) = controller.create_account(email=email,  client=client)

    if status == requests.ConstantsManagement.OK.value:
        return {'msg': 'account created', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.OPERATION_FAILED.value:
        return {'msg': 'operation failed', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NETWORK_ERROR.value:
        return {'msg': 'network error', 'status': status, 'resp': resp}, 200
    
@app.route('/login')
def login():
    args = request.args
    email = args.get('email', type=str)
    ip = args.get('ip', type=str)

    client = ClientSockClass.ClientSocket(ip=ip)

    (status, resp) = controller.connect(email=email,  client=client)

    if status == requests.ConstantsManagement.OK.value:
        return {'msg': 'account created', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.OPERATION_FAILED.value:
        return {'msg': 'operation failed', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NOT_FOUND.value:
        return {'msg': 'not found', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NETWORK_ERROR.value:
        return {'msg': 'network error', 'status': status, 'resp': resp}, 200

@app.route('/searchroutes', methods=['GET'])
def get_routes():
    args = request.args

    match = args.get('match', type=str)
    destination = args.get('destination', type=str)
    ip = args.get('ip',  type=str)
    token = args.get('token',  type=str)

    client = ClientSockClass.ClientSocket(ip=ip)
    client.token = token

    (status, resp) = controller.search_routes(match=match, destination=destination,  client=client)

    if status == requests.ConstantsManagement.OK.value:
        dic = {}
        i = 0
        for  fligth in resp:
            for route in fligth:
                path = utils.Route()
                path.from_string(route)
                dic[i] = {'match':path.match, 'destination':path.destination}
            i+=1


        return {'msg': 'account created', 'status': status, 'resp': dic}, 200
    elif status == requests.ConstantsManagement.OPERATION_FAILED.value:
        return {'msg': 'operation failed', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NOT_FOUND.value:
        return {'msg': 'not found', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NETWORK_ERROR.value:
        return {'msg': 'network error', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.INVALID_TOKEN.value:
        return {'msg': 'invalid token', 'status': status, 'resp': resp}, 200
    
@app.route('/buy', methods=['GET'])
def buy():
    args = request.args

    routes = json.loads(args.get('routes'))
    token = args.get('token',  type=str)
    ip = args.get('ip',  type=str)
    client = ClientSockClass.ClientSocket(ip=ip)
    client.token = token
    list_route = []
    for  route in routes.values():
        path = utils.Route(match=route[0], destination=route[1])
        list_route.append(path.to_string())

    (status, resp) = controller.buy_routes(routes=list_route, client=client)

    if status == requests.ConstantsManagement.OK.value:
        return {'msg': 'Buy complete', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.OPERATION_FAILED.value:
        return {'msg': 'operation failed', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NOT_FOUND.value:
        return {'msg': 'not found', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NETWORK_ERROR.value:
        return {'msg': 'network error', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.INVALID_TOKEN.value:
        return {'msg': 'invalid token', 'status': status, 'resp': resp}, 200

@app.route('/searchboughts', methods=['GET'])
def boughts():
    args = requests.args
    token = args.get('token',  type=str)
    ip = args.get('ip',  type=str)
    client = ClientSockClass.ClientSocket(ip=ip)
    client.token = token

    (status, resp) = controller.search_bougths(client)

    if status == requests.ConstantsManagement.OK.value:
        return {'msg': 'boughts found', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.OPERATION_FAILED.value:
        return {'msg': 'operation failed', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NOT_FOUND.value:
        return {'msg': 'not found', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.NETWORK_ERROR.value:
        return {'msg': 'network error', 'status': status, 'resp': resp}, 200
    elif status == requests.ConstantsManagement.INVALID_TOKEN.value:
        return {'msg': 'invalid token', 'status': status, 'resp': resp}, 200