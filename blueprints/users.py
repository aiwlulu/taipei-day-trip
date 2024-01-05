from flask import Blueprint, request, jsonify
from db import cnxpool
from datetime import datetime, timedelta
import jwt
import os
from werkzeug.security import generate_password_hash, check_password_hash

users_blueprint = Blueprint('users', __name__)

def authenticate_user():
    token = request.headers.get('Authorization')
    if not token:
        return False, "未登入系統，拒絕存取"

    try:
        token = token.split(' ')[1]
        data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])

        return True, data
    except Exception as e:
        print(e)
        return False, "未登入系統，拒絕存取"

@users_blueprint.route('', methods=['POST'])
def register_user():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({'error': True, 'message': '請提供完整的註冊資訊'}), 400

        hashed_password = generate_password_hash(password)

        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT id FROM User WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        cursor.close()
        cnx.close()

        if existing_user:
            return jsonify({'error': True, 'message': '該 Email 已被註冊'}), 400

        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO User (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        cnx.commit()
        cursor.close()
        cnx.close()

        return jsonify({'ok': True}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': True, 'message': '伺服器內部錯誤'}), 500


@users_blueprint.route('/auth', methods=['PUT'])
def login_user():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': True, 'message': '請提供完整的登入資訊'}), 400

        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT id, name, password FROM User WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        cnx.close()

        if not user or not check_password_hash(user[2], password):
            return jsonify({'error': True, 'message': '帳號或密碼錯誤'}), 400

        token = jwt.encode({
            'id': user[0],
            'name': user[1],
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, os.getenv('JWT_SECRET'))

        return jsonify({'token': token}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': True, 'message': '伺服器內部錯誤'}), 500


@users_blueprint.route('/auth', methods=['GET'])
def get_current_user():
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])

        return jsonify({'data': {
            'id': data['id'],
            'name': data['name'],
            'email': data['email']
        }}), 200

    except Exception as e:
        print(e)
        return jsonify({'data': None}), 200
