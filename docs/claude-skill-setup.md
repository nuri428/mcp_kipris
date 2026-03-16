# MCP KIPRIS — Claude Skill 설치 가이드

KIPRIS(한국 지식재산권 정보 서비스) 특허 검색 기능을 Claude Code에 MCP 서버로 등록하는 방법을 안내합니다.

## 사전 준비

### 1. KIPRIS API 키 발급

1. [KIPRIS OpenAPI 포털](https://www.kipris.or.kr/khome/main.do) 접속
2. 회원가입 후 **API 활용 신청** → 키 발급 (무료)
3. 발급된 키를 `.env` 파일에 저장

```bash
# 프로젝트 루트에 .env 파일 생성
echo "KIPRIS_API_KEY=your_api_key_here" > .env
```

### 2. 의존성 설치

Python 3.11+ 및 `uv` 필요

```bash
# uv 설치 (미설치 시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
cd /path/to/mcp_kipris
uv sync
```

---

## 설치 방법

### 방법 A: stdio 방식 (권장)

Claude Code의 `.mcp.json`(프로젝트 범위) 또는 사용자 설정으로 등록합니다.

#### 프로젝트 범위 등록 (`.mcp.json`)

프로젝트 루트에 `.mcp.json` 파일을 생성합니다:

```json
{
  "mcpServers": {
    "kipris": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_kipris.server"],
      "cwd": "/path/to/mcp_kipris",
      "env": {
        "KIPRIS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

> **팁**: API 키를 shell 환경변수로 관리하는 경우 `"KIPRIS_API_KEY": "${KIPRIS_API_KEY}"` 로 설정할 수 있습니다. 단, 해당 환경변수가 반드시 shell에 export되어 있어야 합니다.

#### 사용자 범위 등록 (CLI)

```bash
claude mcp add \
  -e "KIPRIS_API_KEY=your_api_key_here" \
  -s user \
  kipris \
  -- uv --directory /path/to/mcp_kipris run python -m mcp_kipris.server
```

---

### 방법 B: SSE (HTTP) 방식

HTTP 서버를 직접 실행하고 SSE transport로 등록합니다.

#### 1. SSE 서버 실행

```bash
KIPRIS_API_KEY=your_api_key_here uv run python -m mcp_kipris.sse_server \
  --http --port 6274 --host 127.0.0.1
```

백그라운드로 실행하려면:

```bash
KIPRIS_API_KEY=your_api_key_here nohup uv run python -m mcp_kipris.sse_server \
  --http --port 6274 --host 127.0.0.1 > kipris_server.log 2>&1 &
```

#### 2. Claude Code에 등록

```bash
claude mcp add --transport sse -s user kipris http://127.0.0.1:6274/sse
```

---

### 방법 C: mcpo 프록시 방식 (REST API 테스트용)

`mcpo`를 사용하면 `http://localhost:PORT/{tool_name}` 형태의 REST API로 각 툴을 직접 호출할 수 있습니다.

```bash
KIPRIS_API_KEY=your_api_key_here uvx mcpo --port 6275 \
  -- uv --directory /path/to/mcp_kipris run python -m mcp_kipris.server
```

Swagger UI: `http://localhost:6275/docs`

---

## 등록 확인

```bash
claude mcp list
# kipris: ... - ✓ Connected
```

---

## 사용 가능한 툴 (12개)

### 한국 특허 (7개)

| 툴 이름 | 설명 | 필수 파라미터 |
|---------|------|--------------|
| `patent_applicant_search` | 출원인명으로 검색 | `applicant` |
| `patent_free_search` | 키워드(자유검색)로 검색 | `word` |
| `patent_search` | 출원번호로 고급 검색 | `application_number` |
| `patent_application_number_search` | 출원번호 패턴 검색 | `application_number` |
| `patent_righter_search` | 권리자명으로 검색 | `righter_name` |
| `patent_summary_search` | 출원번호로 요약 정보 조회 | `application_number` |
| `patent_detail_search` | 출원번호로 상세 정보 조회 | `application_number` |

### 외국 특허 (5개)

| 툴 이름 | 설명 | 필수 파라미터 |
|---------|------|--------------|
| `foreign_patent_free_search` | 키워드로 외국 특허 검색 | `word` |
| `foreign_patent_applicant_search` | 출원인명으로 외국 특허 검색 | `applicant` |
| `foreign_patent_application_number_search` | 출원번호로 외국 특허 검색 | `application_number` |
| `foreign_international_application_number_search` | 국제출원번호(PCT)로 검색 | `international_application_number` |
| `foreign_international_open_number_search` | 국제공개번호로 검색 | `international_open_number` |

### 지원 국가 (`collection_values`)

`US`(미국), `EP`(유럽), `WO`(PCT), `JP`(일본), `PJ`(일본영문초록), `CP`(중국), `CN`(중국영문초록), `TW`(대만), `RU`(러시아), `CO`(콜롬비아), `SE`(스웨덴), `ES`(스페인), `IL`(이스라엘)

---

## Claude에서 사용 예시

MCP 서버 등록 후 Claude에게 자연어로 질의할 수 있습니다:

```
삼성전자가 출원한 최신 특허 5건 보여줘
인공지능 관련 한국 특허 검색해줘
출원번호 1020200042879 특허의 상세 정보 알려줘
미국 배터리 특허 최신 10건 검색해줘
유럽 반도체 특허 Samsung 출원 목록 보여줘
PCT WO2020100000 특허 내용이 뭐야?
```

---

## 문제 해결

### "there is no result" 반환 시

1. API 키가 올바르게 설정되었는지 확인
2. `.mcp.json`에 환경변수로 `${KIPRIS_API_KEY}`를 사용한 경우, 해당 변수가 shell에 `export`되어 있는지 확인
3. API 키를 직접 값으로 입력하는 방식으로 변경 권장

### MCP 서버 재시작이 필요한 경우

```bash
# 현재 서버 제거 후 재등록
claude mcp remove kipris
claude mcp add -e "KIPRIS_API_KEY=your_key" -s user kipris \
  -- uv --directory /path/to/mcp_kipris run python -m mcp_kipris.server
```

Claude Code를 재시작하면 새로운 프로세스로 서버가 시작됩니다.

### API 키 환경변수 override 문제

`.env` 파일의 API 키가 적용되지 않는 경우, `abs_class.py`와 `server.py`에서 `load_dotenv(override=True)`가 설정되어 있는지 확인합니다. 이 옵션이 없으면 이미 설정된 빈 환경변수를 덮어쓰지 않습니다.

---

## Docker로 실행

```bash
# 이미지 빌드
bash sse_server_build.sh

# 컨테이너 실행
docker run -d \
  -p 6274:6274 \
  -e KIPRIS_API_KEY=your_api_key_here \
  mcp-kipris:latest
```

Claude Code에 등록:

```bash
claude mcp add --transport sse -s user kipris http://localhost:6274/sse
```
