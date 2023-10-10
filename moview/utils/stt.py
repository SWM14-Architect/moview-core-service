import os
import base64
import tempfile
import openai
# from pydub import AudioSegment

from moview.environment.environment_loader import EnvironmentLoader
# from moview.exception.stt_error import AudioTooShortError, AudioTooQuietError

# MIN_LENGTH = 1000
# MIN_DBFS = -40


class SpeechToText:
    @staticmethod
    def file_to_text(audio_file_path):
        openai.api_key = EnvironmentLoader.getenv('openai-api-key')
        audio_file = open(audio_file_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        text = transcript['text']
        return text

    @staticmethod
    def base64_to_text(base64_audio_data):
        openai.api_key = EnvironmentLoader.getenv('openai-api-key')

        # base64 디코딩
        decoded_audio_data = base64.b64decode(base64_audio_data)

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file.write(decoded_audio_data)
            temp_file.flush()
            temp_file_path = temp_file.name

        try:
            # 오디오 길이 또는 레벨 확인
            # audio = AudioSegment.from_file(temp_file_path, format="webm")
            # if len(audio) < MIN_LENGTH:
            #     raise AudioTooShortError()
            # if audio.dBFS < MIN_DBFS:
            #     raise AudioTooQuietError()

            # Whisper API 호출
            with open(temp_file_path, 'rb') as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)

            text = transcript['text']
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        return text


# print(SpeechToText.file_to_text("C:/Users/HYS/Desktop/test.m4a"))
# print(SpeechToText.base64_to_text("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lA1V+pZu3tFdE2my27+nHeF1uz424D4/BrvE6FhAeKRbrTP+9bvG+VL7tpwr///s//d62opeiShjiEc5ljQgQBRuhCaWCqMBUXM2GVetbTNvcuc5//NExB8ROQp4AVtIAIR7PbtQun6au6nFZrpoctChZ8f6//q6bsaAomeITChFIcIuoOxLICAZSbSDTdmbIHZPtTuNLLPP7d36pZh99X5JyqPuv/7+oS+a//iYiY6l+v/+//NExC0diyqkAZhAAK6WN7mZGpcf//6U+KSahZ5h5QqE4Nf///zjBFD90oX0RxwB0pBGNEIecLkf////7B5QNz3k8UU8eY/gHEgRBKGCB4ikiCcKi4oqvZMbEvxWs8iF//NExAkScRawAdhAAHRUgqVIOpcpZ+JxfPcN39YY7zfYUHYdj5JD+RgChiTf/zc96z8GXYee48ycKc4XoVcR/KuSS1atSKfsWdYDT3ZG5p6RIGNwkNJ78NgJy/hPAtJ9//NExBISeRq8AMPYcDYLg7hnO2RobN8v7bYL6aj2pmPZqKAoH5mCte+vX6b5ud79Nbta7m2e4DvCo8FxoqnLO2f////RnfeAeDxmCCtl0EyoUsGYRNOpz8s6cn3r1z52//NExBsSKVa8AMMGlHUdG+ovPeEsKV40DipQjl3N/5MyYyVR1CiyruJEGRN6/SlBMwDjht72f////1L8iBgokjwI8W1EhWxeMMgwUQlKm6rapFRRlYorKF3FccP31obY//NExCUSMQKgAMvYcGScLgAQMomXb1rMzWvbWL7I+sf1aV+yZ+prA7KlXkc8j//YWmsRUyaITEpHnhKFEUcKGQsjQqJgZEOpOBFQvfTc+hlkS52jou1bLKwxW0LlJalt//NExC8SiQaIANPScMN8vW1UtUPIA/w0QioeMELAOsbass5P///51dVEldJivpzBoNUn07gr4BHx/XyQEih5yU0l/WdUspkPymQX8pPAA+pGy59NSjXR9XXXMZUbmIko//NExDcRwQZ0AVpoAMkfQriXmKB7/////////+syIBA2BQDGYQmh1JfASGAJK/SY9m0Wf5ab7WpSfTHiF6BXAi5dUSxcOF43CQhV1D2KjMrL6XlhuZkxBBFlpKSX1UEk//NExEMf0yJwAZloATZaakP/80Tc+gmb//dXUo4aEAvuoxJcef/9ff8wNDVzQuLT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JowTI5ywUgBqoYLIPxYZ3jq0CJ3ms7/+f//7U3tGMUOEuhZKNGugDiIcRxcVULu0JR///+owFSG16HG/fKDY8lrLhXZS6XBy//NExBARmUK0AMvOcNT5QEqhnatMSO0bxpLQnxvkgU7kf4TkhYr039va6FGHnUqjvSj3qjFDx4Xjmvpr////80lIzSqi6SQibAxpLpmcjtGEClt9yrcdE2PnKXNpJsZA//NExBwRgVasAMKElCwNwvGUJIvPFgx///QUYqzIrTSrZuYwMwMIjVDnufD72oR///Ypuzy9yIqhKJIUuRmJeJrlpmZnTX/yns1r///z///+UpkCDvel8LA4wgjV68Dg//NExCkSorq0AGBGuGhHXMi9AggRnM61SJXL//qI+VDDOWxHd+d+3tF8hykL2ooer/////////m3sD/9v/n+ztFzWL9RkXENYER2Bd6K0go5zv92bt8vN16opb5+0bMd//NExDESIma4AAhMufGvYeHnOjjxMvzn/UC55ZeJCs1AqRfKSnQKat0tv5fX////8v53NfF5Of5/2/11TG43lC5ipxnmXmXZM1GqCnkwcSXNPFb3k4eHgsePPFoDE0Xc//NExDsSKfqwABBMmBVw4KYNAWhhXJS0vfE1f+XCN4tYMAFjFYkN6FkjW6oPlVDsrxCO7/cX3/6yOqkWruIUTRKbfPT1boKuLHtjCzwbCVygKdI6Rqzoa/yR5S/Dss7///NExEURgOagAMIEcJFm7djYQnuGFRYptiMEsBTt2jEhJYd48JFJejV2xobmBzeKXzrG2qsHbsNhn/upKTYIUhQJwuPCQFxESk48s8t6zP+xalnviB37ehc0f88kGZG0//NExFIQ2PaIANPScAoE3UosyETllSDjKrp2ysNNtikco6hh1de9mOirM9/5nfsDWridQUiIyFIGw5WBo6HDLeTQrpphxKHE0LhiBwUXjIkTkHRAFMUnQpBAhPp+pTlA//NExGERIPaEANPYcDEc8aeQSmPSqfcUQiqYqD5N/7kda9NstOfmyt1ITXQBgLCmxkjaClr5Pa+/klAxxERAkhhpQGTKGOgQEatA3BzqnxpAumb0puBOXAkqxryJIQzk//NExG8SQP6AAVpgAR2xOOCsTDMSE6lkOMk5EMmtfqGLv6clfEfudMd5T6le3gvdP40Sm6U//pvPz/4m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qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq//NExKwAAANIAAAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq//NExKwAAANIAAAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"))