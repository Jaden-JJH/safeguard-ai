from fastapi import UploadFile
from google.cloud import vision
from config import VISION_CLIENT

async def extract_text_from_image(image_file: UploadFile) -> str:
    """
    업로드된 이미지 파일에서 텍스트를 추출합니다 (OCR).
    """
    # Vision API 클라이언트가 초기화되지 않은 경우
    if VISION_CLIENT is None:
        print("[Error] Vision API 클라이언트가 초기화되지 않았습니다.")
        return ""

    content = await image_file.read()
    image = vision.Image(content=content) # vision은 import google.cloud.vision이 필요함

    print("Cloud Vision API (OCR) 호출 시작...")
    try:
        # config에서 가져온 클라이언트를 사용합니다.
        response = VISION_CLIENT.text_detection(image=image)
        print("OCR API 호출 완료.")
        
        if response.error.message:
            raise Exception(response.error.message)
            
        # full_text_annotation이 없을 경우를 대비한 예외 처리
        if response.full_text_annotation:
            return response.full_text_annotation.text
        else:
            return ""
    except Exception as e:
        print(f"[Error] OCR 실패: {e}")
        return ""