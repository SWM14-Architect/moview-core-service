from moview import app
from flask_cors import CORS

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)
