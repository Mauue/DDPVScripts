import os
import shutil
import uuid

from flask import Flask, render_template, send_from_directory, session, url_for, request
# from flask_socketio import SocketIO, send
# from flask_sockets import Sockets
# from flask_socketio import SocketIO, emit
from gevent.pywsgi import SecureEnviron

from dispatcher.PlannerDispatcher import get_planner_dispatcher, write_rule
from json import dumps, loads, JSONDecodeError

from dispatcher.VerifierDispatcher import get_verifier_dispatcher, VerifierDispatcher
from Planner.fib_manager import read_fib


app = Flask(__name__, static_folder="./static/assets/")
app.config['SECRET_KEY'] = 'secret!'
# sockets = Sockets(app)
# socketio = SocketIO(app)
app.debug = True

settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config")
jar_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tulkun.jar")

#
# @app.route("/Coral")
# def coral_index():
#     return render_template('index.html')


@app.route("/")
def index():
    return render_template('index.html')

# @socketio.on('connect')
# def test_connect():
#     token = str(uuid.uuid1())
#     path = os.path.join(settings_path, token)
#     os.mkdir(path)
#     emit('token', {'data': token})
#     session.
#
#
# @socketio.on('disconnect')
# def test_disconnect():
#     if os.path.exists(path):
#         shutil.rmtree(path)


@app.route('/demo/ws/')
def echo_socket():
    print(request.environ)
    socket = request.environ.get('wsgi.websocket')

    # token = str(uuid.uuid1())
    path = os.path.join(settings_path, "yidongyun")
    # os.mkdir(path)

    while not socket.closed:
        message = socket.receive()
        if message is None:
            break
        try:
            data = loads(message)
            if data["type"] == "genDVNet":
                d = get_planner_dispatcher()
                # topology = data["topology"]
                # edges = [[i["source"], i["target"]] for i in topology]
                # if len(edges) > 20:
                #     return
                socket.send(dumps({"type": "DVNet", "data": d.get_DPVNet(os.path.join(path, "DPVNet.puml"))}))
                # d.new_requirement(edges,
                #                   path,
                #                   data["requirement"],
                #                   handle=lambda t: socket.send(dumps(t))
                #                   )
            elif data["type"] == "start":
                d = get_verifier_dispatcher()
                d.run(path, handle=lambda t: socket.send(dumps(t)))
            elif data["type"] == "getRule":
                res = []
                if "data" in data:
                    res = read_fib(os.path.join(path, "rule"), data["data"])
                socket.send(dumps({"type": "rule", "data": res, "name": data["data"]}))
            elif data["type"] == "setRule":
                dev = data["name"]
                write_rule(os.path.join(path, "rule"), dev, data["data"])
                res = read_fib(os.path.join(path, "rule"), dev)
                socket.send(dumps({"type": "rule", "data": res, "name": dev}))
            else:
                socket.send(dumps({"message": "received!"}))
        except JSONDecodeError:
            print("error", message)
    # os.removedirs(path)
    # if os.path.exists(path):
    #     shutil.rmtree(path)


@app.route("/demo/")
def settings():
    return render_template('demo.html')


@app.route("/origin_check.txt")
def origin_check():
    return send_from_directory('./static/', "origin_check.txt")


if __name__ == "__main__":
    get_verifier_dispatcher()._jar_path = jar_path
    # socketio.run(app)
    import logging
    logging.basicConfig(level=logging.INFO)
    from gevent import pywsgi, ssl
    from geventwebsocket.handler import WebSocketHandler
    environ = SecureEnviron()

    environ.secure_repr = False
    server = pywsgi.WSGIServer(('127.0.0.1', 8080), app, handler_class=WebSocketHandler, environ=environ,
                               )
    print(app.url_map)
    # print(sockets.url_map)
    print('server start')
    server.serve_forever()


