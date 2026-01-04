import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import vision

load_dotenv()

# API 키
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BIGKINDS_API_KEY = os.getenv("BIGKINDS_API_KEY")

# 클라이언트 초기화
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("[Config Warning] GOOGLE_API_KEY가 없습니다.")

# GCP 서비스 클라이언트는 gcloud 인증을 사용하므로 API 키 없이 초기화 가능
#SPEECH_CLIENT = speech.SpeechClient()
#TTS_CLIENT = texttospeech.TextToSpeechClient()
VISION_CLIENT = vision.ImageAnnotatorClient()

# 사용할 Gemini 모델들을 미리 정의
GEMINI_PRO_MODEL = genai.GenerativeModel('gemini-2.5-pro')
GEMINI_FLASH_MODEL = genai.GenerativeModel('gemini-2.5-flash')