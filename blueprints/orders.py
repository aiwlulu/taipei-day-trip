from flask import Blueprint, request, jsonify
from db import cnxpool
from datetime import datetime, timezone
import jwt
import os
import pytz
import requests
from blueprints.bookings import delete_booking
from blueprints.users import authenticate_user

orders_blueprint = Blueprint('orders', __name__)

order_count = 0
current_time = None

@orders_blueprint.route('', methods=['POST'])
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


@orders_blueprint.route('/<orderNumber>', methods=['GET'])
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

