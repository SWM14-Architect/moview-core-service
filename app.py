from moview import app
from flask_cors import CORS

allowed_origins = [
    "http://localhost:3000",
    "https://moview.io",
]

CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)
