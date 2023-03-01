import threading
from flask import Flask, request, jsonify, render_template
from job import run, clear_trigger_condition, add_compare_data, get_diff_info


def create_app():
    app = Flask(__name__)

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
        info = get_diff_info()
        return jsonify({
            "info": info
        })

    @app.route("/")
    def index():
        print("ffff")
        return render_template('index.html')

    
    # threading.Thread(target=run).start()
    
    return app


if __name__ == '__main__':
    create_app().run()
    
    
# cd /home/rabbitlbj/workfolder/stock-monitor ; /usr/bin/env /home/rabbitlbj/workfolder/stock-monitor/venv/bin/python /home/rabbitlbj/.vscode-server/extensions/ms-python.python-2022.17.13051012/pythonFiles/lib/python/debugpy/adapter/../../debugpy/launcher 42105 -- -m flask run --no-debugger --no-reload 
# cd /home/rabbitlbj/workfolder/stock-monitor ; /usr/bin/env /bin/python /home/rabbitlbj/.vscode-server/extensions/ms-python.python-2022.17.13051012/pythonFiles/lib/python/debugpy/adapter/../../debugpy/launcher 40061 -- -m flask run --no-debugger --no-reload 