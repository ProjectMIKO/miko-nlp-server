from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api', methods=['GET'])
def api():
    data = {
        "message": "Hello, API!",
        "status": "success"
    }
    return jsonify(data)

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.json
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
