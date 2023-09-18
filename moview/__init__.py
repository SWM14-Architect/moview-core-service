import random
import string

from flask import Flask
from flask_restx import Api

from moview.controller import interview_controller, input_data_controller, answer_controller, evaluation_controller, \
    feedback_controller
from moview.controller.oauth import oauth_controller

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_letters) for i in range(20))
api = Api(app)

app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지

api.add_namespace(interview_controller.api, '/interview')
api.add_namespace(input_data_controller.api, '/interview')
api.add_namespace(answer_controller.api, '/interview')
api.add_namespace(evaluation_controller.api, '/interview')
api.add_namespace(feedback_controller.api, '/interview')

# oauth api
api.add_namespace(oauth_controller.api, '/interview')
