from flask import Flask
from flask_cors import CORS
from blueprints.pages import pages_blueprint
from blueprints.attractions import attractions_blueprint
from blueprints.users import users_blueprint
from blueprints.bookings import bookings_blueprint
from blueprints.orders import orders_blueprint

app = Flask(__name__, static_url_path='/static')
CORS(app)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.register_blueprint(pages_blueprint)
app.register_blueprint(attractions_blueprint, url_prefix='/api')
app.register_blueprint(users_blueprint, url_prefix='/api/user')
app.register_blueprint(bookings_blueprint, url_prefix='/api/booking')
app.register_blueprint(orders_blueprint, url_prefix='/api/orders')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
