from flask import Flask, jsonify, request, render_template
import pyrebase
import time
import os

config = {
    'apiKey': os.environ.get('API_KEY'),
    "authDomain": os.environ.get('AUTH_DOMAIN'),
    "databaseURL": os.environ.get('DATABASE_URL'),
    "storageBucket": os.environ.get('STORAGE_BUCKET'),
    "serviceAccount": "./account.json"
}

SOFT_TIMELIMIT = 1 # if user was disconnected more then SOFT_TIMELIMIT minutes - status will be 'Connections problems'
HARD_TIMELIMIT = 2 # if user was disconnected more then HARD_TIMELIMIT minutes - there is a high chance that internet is down

firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)

def beautify_time_diff(last_check_timestamp):
    current_timestamp = time.time()
    seconds_since_last_check = current_timestamp - last_check_timestamp

    time_diff_line = ""

    # get count of days:
    days_count = int(seconds_since_last_check // (60 * 60 * 24))

    if days_count:
        time_diff_line += '{} д '.format(days_count)
        seconds_since_last_check = seconds_since_last_check % (60 * 60 * 24)
    
    # get count of hours:
    hours_count = int(seconds_since_last_check // (60 * 60))

    if hours_count:
        time_diff_line += '{} ч '.format(hours_count)
        seconds_since_last_check = seconds_since_last_check % (60 * 60)

    # minutes count:

    minutes_count = int(seconds_since_last_check // 60)

    if minutes_count:
        time_diff_line += '{} м '.format(minutes_count)
        seconds_since_last_check = seconds_since_last_check % 60

    seconds_since_last_check = int(seconds_since_last_check)

    time_diff_line += '{} c'.format(seconds_since_last_check)

    return time_diff_line

def get_current_connection_status(connection):
    last_check_timestamp = connection['last_check']
    stored_status = connection['status']

    if stored_status == 'proper_offline':
        return 'proper_offline'

    current_timestamp = time.time()
    seconds_since_last_check = current_timestamp - last_check_timestamp

    if seconds_since_last_check < SOFT_TIMELIMIT * 60:
        return 'online'
    if seconds_since_last_check > SOFT_TIMELIMIT * 60 and seconds_since_last_check < HARD_TIMELIMIT * 60: 
        return 'connection_problems'
    if seconds_since_last_check >= HARD_TIMELIMIT * 60:
        return 'offline'

def beautify_status(status):
    if status == 'proper_offline':
        return 'Соединение было отключено пользователем'
    if status == 'online':
        return 'Соединение активно'
    if status == 'connection_problems':
        return 'Ожидается подтверждение соединения...'
    if status == 'offline':
        return 'Соединение отсутствует'
    return None

def get_status_text_color(status):
    if status == 'proper_offline':
        return 'gray'
    if status == 'online':
        return 'green'
    if status == 'connection_problems':
        return 'orange'
    if status == 'offline':
        return 'red'
    return None

def get_beautified_connection_data(connection):
    old_status = connection['status']
    current_connection_status = get_current_connection_status(connection)
    current_connection_status_beautified = beautify_status(current_connection_status)
    status_color = get_status_text_color(current_connection_status)
    timediff_line = beautify_time_diff(connection['last_check'])
    return {
        'status_color': status_color,
        'status': current_connection_status_beautified,
        'timediff': timediff_line
    }

@app.route('/healthcheck')
def hello_world():
    return jsonify({'status': 'ok'})

@app.route('/check', methods=['POST'])
def add_new_check():
    if not request.is_json:
        return jsonify({'status': 'cant parse json'})
    data = request.json
    if data.get('uuid', None) is None:
        return jsonify({'status': 'cant parse json'})
    uuid = data.get('uuid')
    
    payload = {
        'last_check': time.time(),
        'status': 'online'
    }
    db.child('connections').child(uuid).set(payload)
    return jsonify({'status': 'ok'})

@app.route('/connections/<uuid>', methods=['GET'])
def get_info_about_connection(uuid):
    connection = db.child('connections').child(uuid).get().val()
    if connection is None:
        return 'Соединения с таким идентификатором не существует'
    
    connection_view_data = get_beautified_connection_data(connection)
    connection_view_data['uuid'] = uuid

    return render_template('connection.html', connection=connection_view_data)


@app.route('/connections/<uuid>', methods=['DELETE'])
def remove_connection(uuid):
    сonnection = db.child('connections').child(uuid).get().val()
    if сonnection is None:
        return 'Соединения с таким идентификатором не существует'
    db.child('connections').child(uuid).remove()

    return 'Соединение удалено'

@app.route('/connections/<uuid>/disable', methods=['POST'])
def disable_connection(uuid):
    сonnection = db.child('connections').child(uuid).get().val()
    if сonnection is None:
        return 'Соединения с таким идентификатором не существует'

    payload = {
        'status': 'proper_offline'
    }
    
    db.child('connections').child(uuid).update(payload)

    return 'Соединение отключено'


@app.route('/')
def connections_list():
    connections = db.child('connections').get()
    
    connections_beautified = []

    for connection in connections.each():
        connection_beautified = get_beautified_connection_data(connection.val())
        connection_beautified['uuid'] = connection.key()
        connections_beautified.append(connection_beautified)

    return render_template('connections_list.html', connections=connections_beautified)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)