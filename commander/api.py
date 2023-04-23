import multiprocessing
from flask import Flask, request, jsonify
import threading

host_name = "0.0.0.0"
port = 5004

app = Flask(__name__)             # create an app instance

APP_VERSION = "1.0.2"

_events_queue: multiprocessing.Queue = None

CONTENT_HEADER = {"Content-Type": "application/json"}

@app.route("/alarm", methods=['GET'])
def update():
    content = request.json


    events = []
    while True:
        try:
            event = _events_queue.get_nowait
            for item in event["alerts"]:
                events.append()
        except Exception as _:

            break
    return jsonify(events)


def start_rest(requests_queue):
    global _requests_queue 
    _requests_queue = requests_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()