from moview import app
from flask_cors import CORS

allowed_origins = [
    "http://localhost:3000",
    "https://moview.io",
]

CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

"""This module patches asyncio to allow nested use of `asyncio.run` and `loop.run_until_complete`."""
__import__("nest_asyncio").apply()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)
