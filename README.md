# Safeguard AI Server

세이프가드 금융사기 시뮬레이션 AI 서버입니다.

## 주요 기능

### 1. 금융사기 시뮬레이션
5가지 유형의 금융사기 시나리오를 제공합니다:
- **보이스피싱**: 검사/경찰 사칭 시나리오
- **전세사기**: 허위 계약 유도 시나리오
- **가족/지인 사칭**: 메신저 피싱 시나리오
- **중고거래 사기**: 안전결제 우회 유도 시나리오
- **로맨스 스캠**: 감정 기반 사기 시나리오

### 2. 적응형 AI 대화
- 사용자의 심리적 취약점을 분석하여 맞춤형 대화 생성
- 텍스트 및 음성 모드 지원
- 실시간 대화 흐름 관리

### 3. 분석 리포트
- **무료 기본 리포트**: 대응 수준 평가 (A/B/C/F), 주의점, 가이드 제공
- **유료 프리미엄 리포트**: 법률적 관점의 심층 분석, 위험 순간 분석, 법률 조언

### 4. 이미지 위험도 진단
- OCR을 통한 이미지 텍스트 추출
- AI 기반 사기 위험도 분석 (위험/주의/관심)
- 실시간 피드백 제공

## 기술 스택

- **Framework**: FastAPI
- **AI Engine**: Google Gemini 2.5 (Pro/Flash)
- **OCR**: Google Cloud Vision API
- **Language**: Python 3.12+
- **Deployment**: Docker

## API 엔드포인트

### 기본
- `GET /` - 서버 상태 확인

### 시뮬레이션
- `POST /simulation/adaptive_turn` - 텍스트 모드 적응형 턴 생성
- `POST /simulation/voice_turn` - 음성 모드 대화 생성

### 분석 리포트
- `POST /analysis/basic_report` - 무료 기본 리포트 생성
- `POST /analysis/premium_report` - 유료 프리미엄 리포트 생성

### 프리미엄 기능
- `POST /diagnose/image` - 이미지 위험도 진단 (OCR + AI 분석)

자세한 API 사용법은 서버 실행 후 `/docs` 페이지를 참고하세요.

## 프로젝트 구조

```
safeguard-ai-server/
├── main.py              # FastAPI 앱 및 라우터
├── config.py            # 환경 설정 및 API 클라이언트 초기화
├── models.py            # Pydantic 데이터 모델
├── services/            # 비즈니스 로직
│   ├── gemini_service.py   # Gemini AI 통합
│   └── ocr_service.py      # Google Vision OCR
├── requirements.txt     # Python 의존성
├── Dockerfile          # Docker 이미지 빌드 설정
├── .env.example        # 환경 변수 템플릿
└── README.md           # 프로젝트 문서
```

## 개발 가이드

### 코드 스타일
- PEP 8 준수
- Type hints 사용 권장

### 새로운 사기 유형 추가
1. `services/gemini_service.py`의 `PERSONA_PROMPTS`에 새로운 시나리오 추가
2. 필요시 `models.py`에 새로운 요청/응답 모델 추가
3. `main.py`에 엔드포인트 추가

### 테스트
```bash
# 서버 상태 확인
curl http://localhost:8000/

# 시뮬레이션 테스트
curl -X POST http://localhost:8000/simulation/adaptive_turn \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.

## 기여

버그 리포트나 기능 제안은 Issues를 통해 제출해주세요.

## 문의

프로젝트 관련 문의사항이 있으시면 Issues를 통해 연락주세요.
