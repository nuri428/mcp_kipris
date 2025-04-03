# MCP KIPRIS

KIPRIS(한국특허정보원) API를 사용하여 특허 정보를 검색하고 조회할 수 있는 MCP(Multi-Channel Platform) 도구입니다.

## 기능

- 한국 특허 검색
  - 출원인 기반 검색
  - 키워드 기반 검색
  - 출원번호 기반 검색
  - 권리자 기반 검색
  - 특허 상세 정보 조회
  - 특허 요약 정보 조회

- 해외 특허 검색
  - 출원인 기반 검색
  - 출원번호 기반 검색
  - 자유 텍스트 검색
  - 국제출원번호 검색
  - 국제공개번호 검색

## 설치 방법

1. Python 3.12 이상이 필요합니다.
2. 가상환경을 생성하고 활성화합니다:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows
```

3. 프로젝트를 설치합니다:
```bash
pip install -e .
```

## 환경 설정

1. KIPRIS API 키 설정:
   - [KIPRIS OpenAPI](https://www.kipris.or.kr/portal/openapi/openApiMainPage.do)에서 API 키를 발급받습니다.
   - 프로젝트 루트에 `.env` 파일을 생성하고 다음과 같이 API 키를 설정합니다:
   ```
   KIPRIS_API_KEY=your_api_key_here
   ```

## 서버 실행 방법

서버는 두 가지 모드로 실행할 수 있습니다:

1. HTTP/SSE 모드:
```bash
python src/mcp_kipris/sse_server.py --http --port 6274
```
- `--port`: 서버 포트 번호 (기본값: 6274)
- `--host`: 바인딩할 호스트 주소 (기본값: 0.0.0.0)

2. stdio 모드:
```bash
python src/mcp_kipris/sse_server.py
```

## API 사용 예제

### SSE 연결 설정

1. SSE 연결 및 세션 ID 받기:
```bash
curl -N http://localhost:6274/messages/
```

응답 예시:
```
event: endpoint
data: /messages/?session_id=<세션_ID>
```

### 도구 목록 조회

```bash
curl http://localhost:6274/tools | jq .
```

### 특허 검색 예제

1. 출원인 검색 (삼성전자의 최근 특허 5건):
```bash
curl -X POST "http://localhost:6274/messages/?session_id=<세션_ID>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "tool",
    "name": "patent_applicant_search",
    "args": {
      "applicant": "삼성전자",
      "docs_count": 5,
      "desc_sort": true
    }
  }'
```

## 지원하는 도구 목록

1. 한국 특허 검색:
   - `patent_applicant_search`: 출원인 기준 검색
   - `patent_keyword_search`: 키워드 기준 검색
   - `patent_search`: 출원번호로 검색
   - `patent_righter_search`: 권리자 기준 검색
   - `patent_application_number_search`: 출원번호로 검색
   - `patent_summary_search`: 출원번호로 요약 정보 검색
   - `patent_detail_search`: 출원번호로 상세 정보 검색

2. 해외 특허 검색:
   - `foreign_patent_applicant_search`: 출원인 기준 검색
   - `foreign_patent_application_number_search`: 출원번호로 검색
   - `foreign_patent_free_search`: 자유 텍스트 검색
   - `foreign_patent_international_application_number_search`: 국제출원번호로 검색
   - `foreign_patent_international_open_number_search`: 국제공개번호로 검색

## 응답 형식

모든 API 응답은 JSON 형식으로 반환되며, 다음과 같은 구조를 가집니다:

```json
[
  {
    "type": "text",
    "text": "검색 결과 텍스트",
    "metadata": null
  }
]
```

## 로깅

서버는 기본적으로 DEBUG 레벨의 로깅을 제공합니다. 로그에서 다음과 같은 정보를 확인할 수 있습니다:
- 도구 호출 시작/완료 시간
- 도구 실행 소요 시간
- 오류 발생 시 상세 정보

## 라이선스

MIT License

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
