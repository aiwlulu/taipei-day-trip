from flask import Blueprint, request, jsonify
from db import cnxpool
from datetime import datetime
import jwt
import os
from blueprints.users import authenticate_user

bookings_blueprint = Blueprint('bookings', __name__)


@bookings_blueprint.route('', methods=['GET'])
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


@bookings_blueprint.route('', methods=['POST'])
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


@bookings_blueprint.route('', methods=['DELETE'])
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
