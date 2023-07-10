import random
import string

from flask import Flask
from flask_restx import Api

from controller import evaluation_controller
from controller import generation_controller


app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_letters) for i in range(20))
api = Api(app)

app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지

api.add_namespace(evaluation_controller.api, '/api')
api.add_namespace(generation_controller.api, '/api')
