import json
import datetime

from flask import Blueprint
from flask import request
from flask import redirect
from flask import abort
from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_current_user

from module import virty
from module import model


app = Blueprint('api', __name__)


@app.route('/api/auth', methods=['POST'])
def api_auth():
    if not request.is_json:
        body = {'message': 'Request type must be JSON'}
        return jsonify(body), 400

    request_body = request.get_json()
    if request_body is None:
        body = {'message': 'Request body is empty'}
        return jsonify(body), 400

    whitelist = {'userid', 'password'}
    if not request_body.keys() <= whitelist:
        body = {'message': 'Missing userid or password in request field'}
        return jsonify(body), 400

    user = model.get_virty_user_class(request_body['userid'])
    if user == None:
        body = {'message': 'Login failure. Bad userid or password'}
        return jsonify(body), 401
    
    if virty.check_password(user.password, request_body['password']) == False:
        body = {'message': 'Login failure. Bad userid or password'}
        return jsonify(body), 401

    expires = datetime.timedelta(days=7)
    token = create_access_token(identity=user.userid, expires_delta=expires)
    body = {'message': 'Login succeeded', 'token': token, 'userid': user.userid, 'isAdmin': user.is_admin}
    return jsonify(body), 200


@app.route('/api/auth/validate', methods=['GET'])
@jwt_required
def api_auth_validate():
    token = request.headers.get("Authorization")
    user = get_current_user()
    return jsonify({'message': 'Validate succeeded', 'token': token, 'userid': user.userid, 'isAdmin': user.is_admin}), 200


@app.route('/api/domain')
@jwt_required
def api_domain():
    domains = model.get_domain()
    return model.make_json_response(domains)

@app.route('/api/domain/<uuid>')
@jwt_required
def api_domain_uuid(uuid):
    domain = model.get_domain_by_uuid(uuid)
    return model.make_json_response(domain)
