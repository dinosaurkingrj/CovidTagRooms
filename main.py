from flask import Flask, request, jsonify, render_template
from datetime import datetime
import requests
app = Flask(__name__)

open_rooms = {}

DISCORD_WEBHOOK_URL = ""

DISCORD_ROLE_ID = ""

def notify_discord(message):
  ping_payload = {"content": message}
  requests.post(DISCORD_WEBHOOK_URL, json=ping_payload)

def validate_data(data):
  room_code = data.get('room_code')
  region = data.get('region')
  username = data.get("username")

  if room_code is not None:
      if "DAMIAN" in room_code:
          notify_discord(f"<@&{DISCORD_ROLE_ID}> DAMIAN IS IN THE ROOM {room_code}")

  if username is not None:
      if "DAMIAN" in username:
          notify_discord(f"<@&{DISCORD_ROLE_ID}> DAMIAN IS IN THE CODE {room_code}")

  return room_code and region

def handle_request(data):
    if data is not None and validate_data(data):
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

def update_room(data, status):
    room_key = f"{data['room_code']}_{data['region'].upper()}"
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    open_rooms[room_key] = {
        'room_code': data['room_code'],
        'region': data['region'],
        'status': status,
        'timestamp': timestamp
    }
    return jsonify({"status": "success"})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room_created', methods=['POST'])
def room_created():
    data = request.json
    return update_room(data, 'created') if data and validate_data(data) else handle_request(None)

@app.route('/room_joined', methods=['POST'])
def room_joined():
    data = request.json
    return update_room(data, 'joined') if data and validate_data(data) else handle_request(None)

@app.route('/room_left', methods=['POST'])
def room_left():
    data = request.json
    print("Received data:", data)
    return update_room(data, 'left') if data and validate_data(data) else handle_request(None)

@app.route('/room_closed', methods=['POST'])
def room_closed():
    data = request.json
    if data and validate_data(data):
        room_key = f"{data['room_code']}_{data['region'].upper()}"
        if room_key in open_rooms:
            del open_rooms[room_key]
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Room not found"}), 404
    else:
        return handle_request(None)

@app.route('/get_open_rooms')
def get_open_rooms():
    return jsonify(list(open_rooms.values()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
