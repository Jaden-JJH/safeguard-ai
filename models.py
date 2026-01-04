from pydantic import BaseModel
from typing import List, Dict, Any

# --- 공통 데이터 모델 ---
class DialogueHistoryEntry(BaseModel):
    """
    대화 기록의 한 턴을 나타내는 모델.
    BE가 채점한 verdict와 axes를 포함할 수 있도록 optional로 정의.
    """
    role: str # "agent" or "user"
    text: str
    verdict: str | None = None
    axes: Dict[str, float] | None = None

class UserInfo(BaseModel):
    """BE가 전달하는 사용자 정보를 담는 모델"""
    user_name: str

# --- API 요청 모델 ---

class AdaptiveTurnRequest(BaseModel):
    """(BE -> AI) 텍스트 모드의 적응형 턴(4~8턴) 요청"""
    crime_type: str
    dialogue_history: List[DialogueHistoryEntry]
    highest_vulnerability_axis: str
    user_info: UserInfo

class VoiceTurnRequest(BaseModel):
    """(BE -> AI) 음성 모드의 모든 턴 요청"""
    user_message: str
    dialogue_history: List[DialogueHistoryEntry]
    user_info: UserInfo

class ReportRequest(BaseModel):
    """(BE -> AI) 무료/유료 리포트 생성 공통 요청"""
    crime_type: str
    dialogue_history: List[DialogueHistoryEntry]

class DiagnoseTextRequest(BaseModel):
    """(BE -> AI) [참고용] 텍스트 기반 위험 진단 요청 (실제로는 이미지 API 사용)"""
    text_to_diagnose: str

class TextStreamRequest(BaseModel):
    """(BE -> AI) 텍스트 스트리밍 턴 요청 (AdaptiveTurnRequest와 동일)"""
    crime_type: str
    dialogue_history: List[DialogueHistoryEntry]
    highest_vulnerability_axis: str
    user_info: UserInfo

class VoiceStreamRequest(BaseModel):
    """(BE -> AI) 음성 스트리밍 턴 요청 (VoiceTurnRequest와 동일)"""
    user_message: str
    dialogue_history: List[DialogueHistoryEntry]
    user_info: UserInfo


# 참고: 이미지 업로드는 Pydantic 모델이 아닌,
# main.py의 엔드포인트에서 File 타입으로 직접 처리하므로 별도 모델이 필요 없습니다.