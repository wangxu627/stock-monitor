from flask import Flask, request, jsonify, redirect
from job import clear_trigger_condition, add_compare_data, get_diff_info
from worker_thread import start_worker_thread

# def create_app():
app = Flask(__name__)
start_worker_thread()

@app.route("/set-code", methods=["POST"])
def set_code():
    data = request.get_json()
    add_compare_data(data)
    return jsonify({"status": "OK"})

@app.route("/clear-cache", methods=["POST"])
def clear_cache():
    clear_trigger_condition()
    return jsonify({"status": "OK"})

@app.route("/get-info")
def get_info():
    include_all = bool(request.args.get("all"))
    info = get_diff_info(include_all)
    return jsonify({
        "info": info
    })

@app.route("/")
def index():
    return ""
