import json
import os
import mysql.connector
from mysql.connector import pooling

dbconfig = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'database': 'TravelEcommerceDB'
}

cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=3, **dbconfig)

current_directory = os.getcwd()
json_file_path = os.path.join(current_directory, 'taipei-attractions.json')

with open(json_file_path, 'r') as f:
    data = json.load(f)

try:
    cnx = cnxpool.get_connection()
    cursor = cnx.cursor()

    for result in data['result']['results']:
        # Insert into Attraction table
        attraction_data = {
            'name': result['name'],
            'category': result['CAT'],
            'description': result['description'],
            'address': result['address'].replace(' ', ''),
            'transport': result['direction'],
            'mrt': result['MRT'],
            'lat': result['latitude'],
            'lng': result['longitude']
        }
        add_attraction = ("INSERT INTO Attraction "
                       "(name, category, description, address, transport, mrt, lat, lng) "
                       "VALUES (%(name)s, %(category)s, %(description)s, %(address)s, %(transport)s, %(mrt)s, %(lat)s, %(lng)s)")
        cursor.execute(add_attraction, attraction_data)
        attraction_id = cursor.lastrowid

        # Insert into AttractionImage table
        images = result['file'].split('https://')
        for image in images:
            if image:
                image_url = 'https://' + image
                extension = image_url.split('.')[-1].lower()
                if extension in ['jpg', 'png']:
                    image_data = {
                        'attraction_id': attraction_id,
                        'image_url': image_url
                    }
                    add_image = ("INSERT INTO AttractionImage "
                               "(attraction_id, image_url) "
                               "VALUES (%(attraction_id)s, %(image_url)s)")
                    cursor.execute(add_image, image_data)

    # Insert into MRTStation table
    for result in data['result']['results']:
        station_name = result.get('MRT', '')
        if station_name:
            cursor.execute('SELECT COUNT(*) FROM MRTStation WHERE name=%s', (station_name,))
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute('INSERT INTO MRTStation (name) VALUES (%s)', (station_name,))
    cnx.commit()

except mysql.connector.Error as err:
    print(f"Something went wrong: {err}")
finally:
    if cursor:
        cursor.close()
    if cnx:
        cnx.close()
