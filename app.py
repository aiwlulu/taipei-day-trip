from flask import *
import os
from mysql.connector import pooling
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime


app = Flask(__name__, static_url_path='/static')
CORS(app)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

dbconfig = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'database': 'TravelEcommerceDB'
}

cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)



# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")


@app.route('/api/attractions')
def get_attractions():
    page = request.args.get('page', default=0, type=int)
    keyword = request.args.get('keyword', default=None, type=str)

    limit = 12
    offset = page * limit

    cnx = cnxpool.get_connection()
    cursor = cnx.cursor()

    query = """
            SELECT
                a.id,
                a.name,
                a.category,
                a.description,
                a.address,
                a.transport,
                a.mrt,
                a.lat,
                a.lng,
                GROUP_CONCAT(ai.image_url) as images
            FROM Attraction a
            LEFT JOIN AttractionImage ai ON a.id = ai.attraction_id
        """
    where_clause = []
    params = []
    if keyword:
        where_clause.append("(a.name LIKE %s OR m.name = %s)")
        params.extend([f"%{keyword}%", keyword])
        query += " LEFT JOIN MRTStation m ON a.mrt = m.name"
    if where_clause:
        query += " WHERE " + " AND ".join(where_clause)
    query += " GROUP BY a.id LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'description': row[3],
            'address': row[4],
            'transport': row[5],
            'mrt': row[6],
            'lat': row[7],
            'lng': row[8],
            'images': row[9].split(',') if row[9] else []
        })

    query = "SELECT COUNT(*) FROM Attraction a"
    where_clause = []
    params = []
    if keyword:
        where_clause.append("(a.name LIKE %s OR m.name = %s)")
        params.extend([f"%{keyword}%", keyword])
        query += " LEFT JOIN MRTStation m ON a.mrt = m.name"
    if where_clause:
        query += " WHERE " + " AND ".join(where_clause)
    
    cursor.execute(query, params)
    total_count = cursor.fetchone()[0]

    if offset + limit < total_count:
        next_page = page + 1
    else:
        next_page = None

    cursor.close()
    cnx.close()

    return jsonify({
        'nextPage': next_page,
        'data': data
    })


@app.route('/api/attraction/<int:attractionId>')
def get_attraction_by_id(attractionId):
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()

        cursor.execute("SET SESSION group_concat_max_len = 65536")

        query = """
            SELECT
                a.id,
                a.name,
                a.category,
                a.description,
                a.address,
                a.transport,
                a.mrt,
                a.lat,
                a.lng,
                GROUP_CONCAT(ai.image_url) as images
            FROM Attraction a
            LEFT JOIN AttractionImage ai ON a.id = ai.attraction_id
            WHERE a.id = %s
            GROUP BY a.id
        """

        params = (attractionId,)
        cursor.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return jsonify({'error': True, 'message': '景點編號不正確'}), 400

        attraction = {
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'description': row[3],
            'address': row[4],
            'transport': row[5],
            'mrt': row[6],
            'lat': row[7],
            'lng': row[8],
            'images': row[9].split(',') if row[9] else []
        }

        cursor.close()
        cnx.close()

        return jsonify({'data': attraction})

    except Exception as e:
        return jsonify({'error': True, 'message': '伺服器內部錯誤'}), 500


@app.route('/api/mrts', methods=['GET'])
def get_mrt_stations_sorted_by_attractions():
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()

        query = """
            SELECT m.name, COUNT(a.id) as attraction_count
            FROM MRTStation m
            LEFT JOIN Attraction a ON m.name = a.mrt
            GROUP BY m.name
            ORDER BY attraction_count DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()        

        mrt_stations = [row[0] for row in rows]

        cursor.close()
        cnx.close()

        return jsonify({'data': mrt_stations})

    except Exception as e:
        return jsonify({'error': True, 'message': '伺服器內部錯誤'}), 500


@app.route('/api/user', methods=['POST'])
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


@app.route('/api/user/auth', methods=['PUT'])
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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, os.getenv('JWT_SECRET'))

        return jsonify({'token': token}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': True, 'message': '伺服器內部錯誤'}), 500


@app.route('/api/user/auth', methods=['GET'])
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="3000")
