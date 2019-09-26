from flask import Flask, make_response, jsonify, request, abort
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin
from werkzeug.security import safe_str_cmp
from modules.database import *
import datetime
import os


def unauthorized():
    """
    Returns response for unauthorized access.
    :return:
    """
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def authenticate(username, password):
    """
    Authenticate user if exists.
    :param username:
    :param password:
    :return:
    """
    user = auth(username, password)

    if user:
        return User(user['id'], user['username'], user['password'])


def identity(payload):
    """
    Get user from payload.
    :param payload:
    :return:
    """
    user_id = payload['identity']

    return get_user_by_id(user_id)


app = Flask(__name__)
app.config['SECRET_KEY'] = get_secret()
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(hours=3)
jwt = JWT(app, authenticate, identity)
cors = CORS(app, supports_credentials=True)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/users', methods=['GET'])
@cross_origin()
@jwt_required()
def users():
    return jsonify(all_users())


@app.route('/users/add', methods=['POST'])
@cross_origin()
@jwt_required()
def add_user():
    if not request.json or 'user' not in request.json:
        abort(400)

    user = request.json['user']

    if 'username' not in user or 'password' not in user:
        abort(400)

    return jsonify(create_user(user['username'], user['password']))


@app.route('/users/edit', methods=['POST'])
@cross_origin()
@jwt_required()
def edit_user():
    if not request.json or 'user' not in request.json:
        abort(400)

    user = request.json['user']

    if 'username' not in user or 'password' not in user or 'id' not in user:
        abort(400)

    return jsonify(update_user(user['id'], user['username'], user['password']))


@app.route('/files', methods=['GET, POST'], defaults={'p': None})
@app.route('/files/<path:p>', methods=['GET, POST'])
@cross_origin()
@jwt_required()
def files(p):
    root_dir = config['root-dir']
    if p is None:
        p = ""
    path = os.path.join(root_dir, p)
    if request.method == "GET":
        if os.path.isdir(path):
            contents = {}
            for f in os.listdir(path):
                if os.path.isfile(os.path.join(path, f)):
                    contents[f] = "file"
                else:
                    contents[f] = "directory"
            return jsonify({"Status": "directory", "data": {"dir": contents}})
        else:
            with open(path, 'r') as rf:
                return jsonify({"Status": "file", "data": {'filename': path, 'contents': rf.read()}})

    else:
        if not request.json or 'contents' not in request.json:
            abort(400)

        if os.path.isfile(path):
            with open(path, 'w') as wf:
                wf.write(request.json['contents'])

            return jsonify({'Status': 'success', "data": {'filename': path, 'contents': request.json['contents']}})
        return jsonify({"Status": "error", "error": "Post is not allowed for directories."})


if __name__ == '__main__':
    app.run()
