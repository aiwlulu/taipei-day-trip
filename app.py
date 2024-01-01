from datetime import datetime, timedelta, timezone
import jwt
import os
from flask import *
from flask_cors import CORS
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
import requests


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
            'exp': datetime.utcnow() + timedelta(days=7)
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


@app.route('/api/booking', methods=['GET'])
def get_unconfirmed_bookings():
    is_authenticated, user_data = authenticate_user()
    if not is_authenticated:
        return jsonify({'error': True, 'message': user_data}), 403

    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """SELECT a.id AS attraction_id, a.name AS attraction_name, a.address AS attraction_address,
                          (
                              SELECT ai.image_url
                              FROM AttractionImage AS ai
                              WHERE ai.attraction_id = a.id
                              LIMIT 1
                          ) AS attraction_image,
                          b.date, b.time, b.price
                   FROM Attraction AS a
                   INNER JOIN Booking AS b ON a.id = b.attraction_id
                   WHERE b.user_id = %s"""
        cursor.execute(query, (user_data['id'],))

        unconfirmed_bookings = cursor.fetchall()

        cursor.close()
        cnx.close()

        if not unconfirmed_bookings:
            return jsonify({'data': None}), 200

        for booking in unconfirmed_bookings:
            booking['time'] = str(booking['time'])

        return jsonify({'data': unconfirmed_bookings}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': True, 'message': '發生內部錯誤'}), 500


@app.route('/api/booking', methods=['POST'])
def create_or_update_booking():
    is_authenticated, user_data = authenticate_user()
    if not is_authenticated:
        return jsonify({'error': True, 'message': "未登入系統，拒絕存取"}), 403

    try:
        data = request.json
        attraction_id = data.get('attractionId')
        date = data.get('date')
        time = data.get('time')
        price = data.get('price')

        if not attraction_id or not date or not time or not price:
            return jsonify({'error': True, 'message': "建立失敗，輸入不正確或其他原因"}), 400

        time_mapping = {
            "morning": datetime.strptime("09:00:00", "%H:%M:%S").time(),
            "afternoon": datetime.strptime("13:00:00", "%H:%M:%S").time(),
        }
        time_value = time_mapping.get(data.get('time'))

        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()

        query_check_existing = """SELECT id FROM Booking 
                                   WHERE user_id = %s"""
        cursor.execute(query_check_existing, (user_data['id'],))
        existing_booking = cursor.fetchone()

        if existing_booking:
            booking_id = existing_booking[0]
            query_update = """UPDATE Booking
                              SET attraction_id = %s, date = %s, time = %s, price = %s
                              WHERE id = %s"""
            cursor.execute(query_update, (attraction_id, date, time_value, price, booking_id))
        else:
            query_insert = """INSERT INTO Booking (user_id, attraction_id, date, time, price)
                              VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query_insert, (user_data['id'], attraction_id, date, time_value, price))

        cnx.commit()
        cursor.close()
        cnx.close()

        return jsonify({'ok': True}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': True, 'message': "伺服器內部錯誤"}), 500


@app.route('/api/booking', methods=['DELETE'])
def delete_booking():
    is_authenticated, user_data = authenticate_user()
    if not is_authenticated:
        return jsonify({'error': True, 'message': "未登入系統，拒絕存取"}), 403

    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        query = "DELETE FROM Booking WHERE user_id = %s"
        cursor.execute(query, (user_data['id'],))
        cnx.commit()
        cursor.close()
        cnx.close()

        return jsonify({'ok': True}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': True, 'message': "伺服器內部錯誤"}), 500


order_count = 0
current_time = None

@app.route('/api/orders', methods=['POST'])
def create_orders():
    global order_count, current_time

    is_authenticated, user_data = authenticate_user()
    if not is_authenticated:
        return jsonify({'error': True, 'message': "未登入系統，拒絕存取"}), 403

    data = request.get_json()
    prime = data.get('prime')
    order = data.get('order')

    if not prime or not order:
        return jsonify({'error': True, 'message': "建立失敗，輸入不正確或其他原因"}), 400

    taiwan_tz = pytz.timezone('Asia/Taipei')
    taiwan_time = datetime.now(timezone.utc).astimezone(taiwan_tz)

    if current_time is None or taiwan_time != current_time:
        order_count = 0
        current_time = taiwan_time

    order_count += 1
    order_count_str = str(order_count).zfill(3)
    order_number = taiwan_time.strftime("%Y%m%d%H%M%S") + order_count_str

    payment_status = 1  # Default to unpaid

    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()

        query_insert_order = """INSERT INTO `Order` (user_id, order_number, prime, price, attraction_id, 
                                                     date, time, contact_name, contact_email, 
                                                     contact_phone, payment_status)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        cursor.execute(query_insert_order, (user_data['id'], order_number, prime, order['price'], order['attractionId'],
                                            order['date'], order['time'], order['contact']['name'], 
                                            order['contact']['email'], order['contact']['phone'], payment_status))

        # TapPay
        tappay_api_url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
        tappay_api_key = os.getenv('TAPPAY_API_KEY')

        tappay_data = {
            "prime": prime,
            "partner_key": tappay_api_key,
            "merchant_id": "aiwlulu_TAISHIN",
            "details": "TapPay Test",
            "amount": order['price'],
            "cardholder": {
                "phone_number": "+886" + order['contact']['phone'][1:],
                "name": order['contact']['name'],
                "email": order['contact']['email']
            }
        }

        tappay_headers = {
            "Content-Type": "application/json",
            "x-api-key": tappay_api_key
        }

        response = requests.post(tappay_api_url, json=tappay_data, headers=tappay_headers)
        tappay_response = response.json()

        if tappay_response.get('status') == 0:
            payment_status = 0
            delete_booking()
        else:
            pass

        query_update_payment_status = """UPDATE `Order` SET payment_status = %s WHERE order_number = %s"""
        cursor.execute(query_update_payment_status, (payment_status, order_number))

        cnx.commit()
        cursor.close()
        cnx.close()

        return jsonify({'message': 'Order created successfully', 'order_number': order_number, 'payment_status': payment_status}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': True, 'message': "伺服器內部錯誤"}), 500


@app.route('/api/order/<orderNumber>', methods=['GET'])
def get_order(orderNumber):
    is_authenticated, user_data = authenticate_user()
    if not is_authenticated:
        return jsonify({'error': True, 'message': "未登入系統，拒絕存取"}), 403

    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()

        query_get_order = """SELECT `Order`.*, `Attraction`.`name`, `Attraction`.`address`, `AttractionImage`.`image_url`
                             FROM `Order`
                             JOIN `Attraction` ON `Order`.`attraction_id` = `Attraction`.`id`
                             JOIN `AttractionImage` ON `Order`.`attraction_id` = `AttractionImage`.`attraction_id`
                             WHERE `Order`.`order_number` = %s
                             LIMIT 1"""
        cursor.execute(query_get_order, (orderNumber,))

        order_data = cursor.fetchone()

        if order_data is None:
            return jsonify({'data': None}), 200

        if order_data[1] != user_data['id']:
            return jsonify({'error': True, 'message': "非訂單所有者，故無法查詢此訂單資訊"}), 403

        order_info = {
            "number": order_data[2],
            "price": order_data[4],
            "trip": {
                "attraction": {
                    "id": order_data[0],
                    "name": order_data[12],
                    "address": order_data[13],
                    "image": order_data[14]
                },
                "date": str(order_data[6]),
                "time": order_data[7]
            },
            "contact": {
                "name": order_data[8],
                "email": order_data[9],
                "phone": order_data[10]
            },
            "status": order_data[11]
        }

        cnx.commit()
        cursor.close()
        cnx.close()

        return jsonify({'data': order_info}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': True, 'message': "伺服器內部錯誤"}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="3000")
