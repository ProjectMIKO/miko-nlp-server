from flask import Flask
from flask_cors import CORS
from nlp_keyword.controller import keyword

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)

app.register_blueprint(keyword, url_prefix='/api/keyword')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
