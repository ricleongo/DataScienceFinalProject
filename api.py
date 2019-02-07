from flask import Flask, jsonify, render_template, request, send_from_directory
import json

app = Flask(__name__, static_url_path = "")

@app.route("/api/user")
def user():
    return send_from_directory('raw_data', 'user.json')

@app.route("/api/business")
def business():
    return send_from_directory('raw_data', 'business.json')

@app.route("/api/checkin")
def checkin():
    return send_from_directory('raw_data', 'checkin.json')

@app.route("/api/photo")
def photo():
    return send_from_directory('raw_data', 'photo.json')

@app.route("/api/review")
def review():
    return send_from_directory('raw_data', 'review.json')

@app.route("/api/tip")
def tip():
    return send_from_directory('raw_data', 'tip.json')



if __name__ == '__main__':
    app.run(debug=True)