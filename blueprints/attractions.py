from flask import Blueprint, request, jsonify
from db import cnxpool

attractions_blueprint = Blueprint('attractions', __name__)

@attractions_blueprint.route('/attractions')
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

@attractions_blueprint.route('/attraction/<int:attractionId>')
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

@attractions_blueprint.route('/mrts', methods=['GET'])
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
