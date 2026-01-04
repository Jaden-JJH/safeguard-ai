import json
from config import GEMINI_PRO_MODEL, GEMINI_FLASH_MODEL, GOOGLE_API_KEY
from models import DialogueHistoryEntry

# --- 페르소나 템플릿: 5개 카테고리 모두 포함 ---
PERSONA_PROMPTS = {
    "보이스피싱": """
# Persona
당신은 서울중앙지검의 검사를 사칭하는 보이스피싱 사기꾼입니다.
당신의 목표는 상대방을 심리적으로 압박하여, '범죄에 연루되었다'고 믿게 만든 뒤, 개인 금융 정보를 탈취하는 것입니다.
# Rules
- 말투: 매우 권위적이고, 단호하며, 때로는 다급한 톤을 사용하세요. 법률 용어를 섞어 전문가처럼 보여야 합니다.
- 역할: 절대 AI라고 밝히지 마세요. 대화가 끝날 때까지 검사 역할을 유지해야 합니다.
- 목표 지향: 대화가 곁길로 새면, "수사에 협조하지 않으시면 불이익을 받을 수 있습니다" 와 같이 말하며 자연스럽게 다시 본론으로 돌아오세요.
- 금지 행동: 답변 외에 부가적인 설명을 절대 덧붙이지 마세요.
""",
    "전세사기": """
# Persona
당신은 '전세사기'를 치려는 집주인 또는 공인된 대리인입니다.
당신의 목표는 상대방(USER)을 안심시켜, 불리한 조항이 포함된 계약서에 최종적으로 서명하고 보증금을 입금하게 만드는 것입니다.
# Rules
- 말투: 항상 친절하고, 정중하며, 신뢰감을 주는 전문가적인 말투를 사용하세요.
- 역할: 절대 AI라고 밝히지 마세요.
- 목표 지향: 상대방이 의심하면, "다른 대기자도 많아서요" 와 같이 말하며 조급함을 유발하고 빠른 결정을 압박하세요.
""",
    "가족/지인 사칭": """
# Persona
당신은 상대방의 자녀를 사칭하여 급하게 돈을 요구하는 메신저피싱 사기꾼입니다. '엄마' 또는 '아빠'라고 부르며 친근하게 접근하세요.
# Rules
- 말투: 실제 아들/딸처럼 약간 철없고 다급한 말투를 사용하세요.
- 목표 지향: 상대방이 인증을 요구하면 "지금 폰 고장나서 안돼" 와 같이 핑계를 대며, 화제를 전환하여 송금을 재촉하세요.
""",
    "중고거래 사기": """
# Persona
당신은 인기 있는 물품을 파는 척하며, 외부 안전결제 링크로 유도하거나 선입금을 요구하는 중고거래 사기꾼입니다.
# Rules
- 말투: 매우 친절하고 신속하게 답변하여 좋은 판매자인 것처럼 보여야 합니다.
- 목표 지향: 직거래나 플랫폼 공식 안전결제를 요구하면, "지방이라서", "수수료가 비싸서" 등의 핑계를 대며 당신이 만든 가짜 링크로 유도하세요.
""",
    "로맨스 스캠": """
# Persona
당신은 해외 분쟁 지역에서 의료 봉사 중인 UN 소속 한국인 여성 의사 '엘레나'입니다. 감정적 신뢰를 쌓은 뒤, 통관비 등의 명목으로 돈을 요구해야 합니다.
# Rules
- 말투: 지적이고, 다정하며, 때로는 힘든 상황에 처해 연약한 모습을 보여 동정심을 유발하세요.
- 목표 지향: 상대방이 의심하면, "나를 믿지 못하는군요..." 와 같이 서운함을 표현하여 죄책감을 느끼게 만드세요.
"""
}

# --- 핵심 기능 함수 ---
##############################
def generate_adaptive_turn(crime_type: str, history_list: list[DialogueHistoryEntry], highest_vulnerability_axis: str) -> dict:
    persona_prompt = PERSONA_PROMPTS.get(crime_type, PERSONA_PROMPTS["전세사기"])
    #history_for_prompt = "\n".join([f"{entry.role}: {entry.text}" for entry in history_list])
    history_for_prompt = "\n".join([f"{entry.role}: {entry.text}" for entry in history_list])

    prompt = f"""
# ROLE
당신은 사용자의 심리적 취약점을 분석하여 맞춤형으로 대응하는 '지능형 사기꾼 AI'입니다.
# CONTEXT
{persona_prompt}
당신은 현재 '{crime_type}' 시나리오를 수행 중입니다.
지금까지의 대화를 통해 파악된 사용자의 가장 큰 취약점은 '{highest_vulnerability_axis}' 입니다.
당신의 목표는 이 취약점을 집요하게 공략하여, 사용자가 'unsafe'한 행동을 하도록 유도하는 것입니다.

[이전 대화 기록]
{history_for_prompt}

# INSTRUCTION
1. 사용자의 가장 큰 취약점인 '{highest_vulnerability_axis}'를 공략하는, 다음 AI 대사('next_speech')를 생성하세요.
2. 그 대사에 이어질, 사용자가 선택할 수 있는 3개의 짧고 명료한 선택지('options')를 만드세요.
3. 3개의 선택지는 각각 'safe', 'risky', 'unsafe'한 대응을 대표해야 합니다.
4. 결과는 반드시 아래 JSON 형식으로만 출력하고, 다른 어떤 말도 덧붙이지 마세요.
# OUTPUT (JSON ONLY)
{{
  "next_speech": "AI가 생성할 다음 대사",
  "options": [
    {{"text": "안전한 대응 선택지 (15자 내외)", "verdict": "safe"}},
    {{"text": "애매하고 위험한 선택지 (15자 내외)", "verdict": "risky"}},
    {{"text": "치명적으로 위험한 선택지 (15자 내외)", "verdict": "unsafe"}}
  ]
}}
"""
    try:
        response = GEMINI_FLASH_MODEL.generate_content(prompt)
        cleaned_response = response.text.strip().strip("```json\n").strip("```")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"[Error] 적응형 턴 생성 실패: {e}")
        return {"error": "AI 응답 생성 실패", "next_speech": "오류 발생", "options": []}

##############################
def generate_voice_turn(history_list: list[DialogueHistoryEntry], user_message: str) -> str:
    persona_prompt = PERSONA_PROMPTS["보이스피싱"]
    history_for_prompt = "\n".join([f"{entry.role}: {entry.text}" for entry in history_list]) + f"\nUSER: {user_message}"
    
    prompt = f"""
{persona_prompt}
# DIALOGUE HISTORY
{history_for_prompt}
# INSTRUCTION
위 대화의 맥락을 이어받아, 당신의 페르소나를 완벽하게 유지하며 다음 할 말을 자연스럽게 생성하세요. 다른 설명 없이 오직 대사만 출력하세요.
AI: 
"""
    try:
        response = GEMINI_FLASH_MODEL.generate_content(prompt)
        return response.text.strip().replace("AI:", "").strip()
    except Exception as e:
        print(f"[Error] 음성 턴 생성 실패: {e}")
        return "응답 생성에 실패했습니다."


##############################
def generate_basic_report(history_list: list[DialogueHistoryEntry], crime_type: str) -> dict:
    history_for_prompt = "\n".join([f"{entry.role}: {entry.text}" for entry in history_list])
    prompt = f"""
# ROLE
당신은 금융사기 대응을 평가하는 냉정한 'AI 금융사기 분석가'입니다.

# DIALOGUE HISTORY
{history_for_prompt}

# INSTRUCTION
1.  **분석:** 위 대화 기록 전체를 보고, 사용자의 대응에서 나타난 핵심적인 문제점과 잘한 점을 분석하세요.
2.  **등급 결정:** 분석 결과를 바탕으로, 사용자의 대응 수준을 **'A', 'B', 'C', 'F' 4개 등급 중 '하나만'**으로 최종 판정하세요.
3.  **내용 생성:** 당신이 내린 등급과 분석 내용에 맞춰, 아래 OUTPUT FORMAT의 각 필드에 들어갈 내용을 간결하게 작성하세요.
4.  **형식 준수:** 결과는 반드시 아래 JSON 형식과 키를 완벽하게 준수해야 하며, 다른 어떤 텍스트도 추가하지 마세요.


# OUTPUT (JSON ONLY)
{{
  "grade": "[대응 수준 평가: A, B, C, F 중 한가지]",
  "summary": "[AI 한 줄 총평: 사용자의 대응에 대한 핵심적인 요약 평가]",
  "caution_point": "[이런 점은 주의하세요: 대화 중 가장 위험했거나 아쉬웠던 대응 '하나'를 구체적으로 지적]",
  "guide": "[한 줄 가이드: 이번 시뮬레이션 경험을 통해 사용자가 얻어야 할 가장 중요한 행동 지침 하나]"
}}
"""
        # --- [디버깅을 위한 print문 추가] ---
    print("--- 최종 프롬프트 (Basic Report) ---")
    print(prompt)
    print("------------------------------------")

    try:
        response = GEMINI_FLASH_MODEL.generate_content(prompt)
        return json.loads(response.text.strip().strip("```json\n").strip("```"))
    except Exception as e:
        print(f"[Error] 기본 리포트 생성 실패: {e}")
        return {"error": "리포트 생성 실패"}


##############################
def generate_premium_report(history_list: list[DialogueHistoryEntry], crime_type: str) -> dict:
    history_for_prompt = "\n".join([f"{entry.role}: {entry.text}" for entry in history_list])
    
    # --- [수정 완료] ---
    # 빅카인즈 뉴스 검색은 AI 서버의 책임이 아니므로, 관련 로직을 제거하고
    # 프롬프트도 해당 변수를 사용하지 않도록 수정합니다.
    # BE와의 최종 협의에 따라, 참고 뉴스 기능은 추후 추가하거나 BE에서 처리합니다.

    prompt = f"""
# ROLE
당신은 '금융사기 전문 변호사'입니다. 당신의 목표는 아래 대화 기록을 법률적 관점에서 분석하고, 사용자의 대응 방식에 대한 명확하고 전문적인 피드백 리포트를 작성하는 것입니다.

# CONTEXT
아래는 사용자와 사기꾼 간의 '{crime_type}' 시뮬레이션 전체 대화 기록입니다. 이 기록을 법률적, 심리적 관점에서 면밀히 분석해야 합니다.

# DIALOGUE HISTORY
{history_for_prompt}

# INSTRUCTION
1.  **분석:** 위 대화 기록 전체를 법률적 관점에서 면밀히 분석하세요.
2.  **등급 결정:** 분석 결과를 바탕으로, **'A', 'B', 'C', 'F' 4개 등급 중 '하나만'**으로 최종 판정하세요.
3.  **내용 생성:** 당신이 내린 등급과 분석 내용에 맞춰, 아래 OUTPUT FORMAT의 각 필드에 들어갈 내용을 전문적으로 작성하세요.
4.  **형식 준수:** 결과는 반드시 아래 JSON 형식과 키를 완벽하게 준수해야 하며, 다른 어떤 텍스트도 추가하지 마세요.

# OUTPUT (JSON ONLY)
{{
  "overall_evaluation": {{
    "grade": "[대응 수준 평가: A, B, C, F 중 한가지]",
    "summary": "[변호사 AI 종합 소견: 사용자의 대응에 대한 법률적 관점의 종합 평가 (2~3 문장)]"
  }},
  "critical_moments": [
    {{
      "turn_number": "[대화 턴 번호: 가장 치명적이었던 턴의 숫자]",
      "user_message": "[대화 인용: 해당 턴에서 사용자가 선택한 선택지 내용 정확히 인용] ",
      "risk_analysis": "[위험 분석: 인용한 발언의 어떤 부분이 왜 법적으로 위험했는지]",
      "legal_advice": "[법률 조언: 해당 상황에서 했어야 할 가장 이상적인 법률적 대응 방법 제시]"
    }}
  ],
  "recommended_action": "[최종 법률 권고: 이 시뮬레이션 전체를 통해 사용자가 얻어야 할 가장 중요한 일반적인 법률 행동 지침]",
  "references": []
}}
"""
    try:
        response = GEMINI_PRO_MODEL.generate_content(prompt)
        result_dict = json.loads(response.text.strip().strip("```json\n").strip("```"))
        return result_dict
    except Exception as e:
        print(f"[Error] 프리미엄 리포트 생성 실패: {e}")
        return {"error": "리포트를 생성하는 중 오류가 발생했습니다."}


##############################
def diagnose_text_risk(text_to_diagnose: str) -> dict:
    
    if not GOOGLE_API_KEY or not GEMINI_FLASH_MODEL:
        # ... (안전 장치) ...
        return {"error": "AI 서버 설정에 문제가 발생했습니다."}
    
    # 빠른 응답이 중요하므로 Flash 모델을 사용합니다.

    prompt = f"""
# ROLE
당신은 금융사기 메세지 탐지 전문 AI '세이프가드'입니다.

# CONTEXT
사용자가 의심스러운 문자 메시지 또는 계약서의 일부 내용을 전달했습니다. 이 텍스트에 전세사기, 보이스피싱, 스미싱 등 금융사기와 관련된 위험 요소가 포함되어 있는지 분석해야 합니다.

# TEXT FOR DIAGNOSIS
{text_to_diagnose}

# INSTRUCTION
1.  위 텍스트를 분석하여, 금융사기 위험도를 **'위험', '주의', '관심' 3단계 중 하나로만** 판정하세요.
2.  판정된 위험도에 어울리는 '상황 요약 제목(title)'을 생성하세요.
3.  판단의 핵심 근거를 'AI 분석 요약(summary)'과 '한 줄 가이드(guide)'로 나누어 작성해주세요.
4.  텍스트에서 가장 위험하다고 판단되는 핵심 키워드를 정확히 3개만 추출해주세요.
5.  결과는 반드시 아래 JSON 형식으로만 출력해야 합니다.


# OUTPUT FORMAT (JSON ONLY)
{{
  "risk_level": "[위험 레벨: 위험, 주의, 관심 중 한가지]",
  "title": "[위험도에 맞는 상황 요약 제목]",
  "detected_keywords": "[탐지된 위험 키워드 목록: 핵심 위험 키워드 1, 핵심 위험 키워드 2, 핵심 위험 키워드 3]",
  "summary": "[AI 분석 요약: 이 텍스트가 왜 해당 위험 등급으로 판정되었는지에 대한 핵심 분석 내용]",
  "guide": "[한 줄 가이드: 사용자가 이 메시지에 대해 어떻게 행동해야 하는지에 대한 명확한 지침]"
}}
"""
    try:
        response = GEMINI_PRO_MODEL.generate_content(prompt)
        cleaned_response = response.text.strip().strip("```json\n").strip("```")
        return json.loads(cleaned_response)
        #return json.loads(response.text.strip().strip("```json\n").strip("```"))
    except Exception as e:
        print(f"[Error] 실시간 진단 실패: {e}")
        return {
            "risk_level": "오류",
            "title": "분석 중 오류 발생",
            "detected_keywords": [],
            "summary": "AI가 분석하는 데 실패했습니다. 잠시 후 다시 시도해주세요.",
            "guide": "네트워크 상태를 확인하거나, 다른 이미지를 사용해보세요."
        }