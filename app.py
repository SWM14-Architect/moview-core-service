from moview import app
from flask_cors import CORS
from moview.config.jwt.jwt_config import JWTConfig
from flask_jwt_extended import JWTManager

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)


def set_jwt_config():
    app.config['JWT_SECRET_KEY'] = JWTConfig.get_jwt_secret_key()
    app.config['JWT_TOKEN_LOCATION'] = JWTConfig.get_jwt_location()
    app.config['JWT_COOKIE_SECURE'] = JWTConfig.get_jwt_cookie_secure()
    app.config['JWT_COOKIE_CSRF_PROTECT'] = JWTConfig.get_jwt_cookie_csrf_protect()
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWTConfig.get_jwt_access_token_expires()
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWTConfig.get_jwt_refresh_token_expires()
    JWTManager(app)


if __name__ == '__main__':
    set_jwt_config()
    app.run(host="0.0.0.0", port=5005, debug=True)
