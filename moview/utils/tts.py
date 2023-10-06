import requests
import json

from moview.environment.environment_loader import EnvironmentLoader


class TextToSpeech:
    @staticmethod
    def text_to_base64(text) -> str:
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={EnvironmentLoader.getenv('google-cloud-api-key')}"
        payload = {
            "input": {"text": text},
            "voice": {"language_code": "ko-KR", "name": "ko-KR-Neural2-C"},
            "audioConfig": {"audioEncoding": "MP3"}
        }

        response = requests.post(url, json=payload)
        audio_data = json.loads(response.text)['audioContent']
        return audio_data
