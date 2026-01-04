import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends

# --- 1. 역할별 전문가(모듈) 및 모델 import ---
from services import gemini_service, ocr_service
from models import (
    AdaptiveTurnRequest, VoiceTurnRequest, ReportRequest,
    DialogueHistoryEntry, UserInfo # 상세 모델 import
)

# --- 2. FastAPI 앱 생성 ---
app = FastAPI(
    title="Safeguard AI Server",
    description="금융사기 시뮬레이션을 위한 AI 서버 API (v3.0 - Adaptive Engine)",
    version="3.0.0"
)

# --- 3. API 엔드포인트 ---

@app.get("/", tags=["기본"])
def read_root():
    """서버 상태 확인용 기본 엔드포인트"""
    return {"status": "ok", "message": "Safeguard AI Server is running."}


@app.post("/simulation/adaptive_turn", tags=["시뮬레이션"])
def handle_adaptive_turn(request: AdaptiveTurnRequest):
    """
    (BE 전용) 텍스트 모드의 적응형 턴(4~8턴)을 위한 다음 대사와 선택지를 생성합니다.
    - 입력: crime_type, 대화 기록, 최대 취약점
    - 출력: { "next_speech": "...", "options": [...] }
    """
    return gemini_service.generate_adaptive_turn(
        crime_type=request.crime_type,
        history_list=request.dialogue_history,
        highest_vulnerability_axis=request.highest_vulnerability_axis
    )


@app.post("/simulation/voice_turn", tags=["시뮬레이션"])
def handle_voice_turn(request: VoiceTurnRequest):
    """
    (BE 전용) 음성 모드의 다음 턴을 위한 AI 대사(텍스트)를 생성합니다.
    - 입력: 대화 기록, 사용자의 STT 변환 텍스트
    - 출력: { "ai_message": "..." }
    """
    ai_message = gemini_service.generate_voice_turn(
        history_list=request.dialogue_history,
        user_message=request.user_message
    )
    return {"ai_message": ai_message}

@app.post("/analysis/basic_report", tags=["리포트"])
def get_basic_report(request: ReportRequest):
    # 1. 먼저, gemini_service.generate_basic_report 함수를 호출하고,
    #    그 결과를 'report_data'라는 변수에 '일단 저장'합니다.
    report_data = gemini_service.generate_basic_report(
        crime_type=request.crime_type,
        history_list=request.dialogue_history
    )

    # 2. 저장된 'report_data'를 '검사'합니다.
    VALID_GRADES = {"A", "B", "C", "F"}
    if report_data.get("grade") not in VALID_GRADES:
        # 3. 만약 검사 결과 문제가 있다면, 'report_data'를 '수정'합니다.
        report_data["grade"] = "C"
        print(f"[Warning] Basic report's grade was invalid. Corrected to 'C'.")
    
    # 4. 검사와 수정이 모두 끝난, 완벽한 'report_data'를 최종적으로 return 합니다.
    return report_data

@app.post("/analysis/premium_report", tags=["리포트"])
def get_premium_report(request: ReportRequest):
    """
    (BE 전용) 시뮬레이션 종료 후, 유료 심층 분석 리포트를 생성합니다.
    """
    # 1. gemini_service.generate_premium_report 함수를 호출하고,
    #    그 결과를 'report_data' 변수에 저장합니다.
    report_data = gemini_service.generate_premium_report(
        crime_type=request.crime_type,
        history_list=request.dialogue_history
    )

    # 2. 저장된 'report_data'를 '검사'합니다.
    VALID_GRADES = {"A", "B", "C", "F"}
    # 중첩된 JSON 구조 안의 grade 키를 안전하게 확인합니다.
    if report_data.get("overall_evaluation", {}).get("grade") not in VALID_GRADES:
        # 3. 만약 문제가 있다면, 'report_data'를 '수정'합니다.
        #    overall_evaluation 키가 없을 경우를 대비하여 기본값을 설정해줍니다.
        if "overall_evaluation" not in report_data:
            report_data["overall_evaluation"] = {}
        report_data["overall_evaluation"]["grade"] = "C"
        print(f"[Warning] Premium report's grade was invalid. Corrected to 'C'.")
    
    # 4. 검사와 수정이 모두 끝난, 완벽한 'report_data'를 최종적으로 return 합니다.
    return report_data

# @app.post("/analysis/basic_report", tags=["리포트"])
# def get_basic_report(request: ReportRequest):
#     """
#     (BE 전용) 시뮬레이션 종료 후, 무료 기본 리포트를 생성합니다.
#     - 입력: crime_type, 전체 대화 기록
#     - 출력: { "grade": "...", "summary": "...", ... }
#     """
#     return gemini_service.generate_basic_report(
#         crime_type=request.crime_type,
#         history_list=request.dialogue_history
#     )


# @app.post("/analysis/premium_report", tags=["리포트"])
# def get_premium_report(request: ReportRequest):
#     """
#     (BE 전용) 시뮬레이션 종료 후, 유료 심층 분석 리포트를 생성합니다.
#     - 입력: crime_type, 전체 대화 기록
#     - 출력: { "overall_evaluation": {...}, "critical_moments": [...], ... }
#     """
#     return gemini_service.generate_premium_report(
#         crime_type=request.crime_type,
#         history_list=request.dialogue_history
#     )


@app.post("/diagnose/image", tags=["프리미엄"])
async def diagnose_image_risk(image_file: UploadFile = File(...)):
    """
    (BE 전용) 이미지 파일을 받아 OCR로 텍스트를 추출하고, 위험도를 분석합니다.
    - 입력: 이미지 파일
    - 출력: { "risk_level": "...", "reason": "...", ... }
    """
    # 1. OCR 전문가에게 이미지 분석 요청
    extracted_text = await ocr_service.extract_text_from_image(image_file)
    
    if not extracted_text:
        return {
            "risk_level": "안전",
            "reason": "이미지에서 분석할 텍스트를 찾을 수 없습니다.",
            "detected_keywords": [],
            "extracted_text": ""
        }

    # 2. Gemini 전문가에게 텍스트 위험도 진단 요청
    diagnosis_result = gemini_service.diagnose_text_risk(extracted_text)
    
    # 3. OCR로 추출한 원본 텍스트를 결과에 포함하여 반환
    diagnosis_result["extracted_text"] = extracted_text
    
    return diagnosis_result