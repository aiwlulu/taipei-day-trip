from flask import Blueprint, render_template

pages_blueprint = Blueprint('pages', __name__)

@pages_blueprint.route("/")
def index():
    return render_template("index.html")

@pages_blueprint.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")

@pages_blueprint.route("/booking")
def booking():
    return render_template("booking.html")

@pages_blueprint.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@pages_blueprint.route("/history")
def history():
    return render_template("history.html")
