# MCP Kipris

MCP Server를 통해 Kipris Plus에서 제공하는 특허 검색 API를 쉽게 사용할 수 있는 Python 패키지입니다.

## 설치 방법

```bash
pip install mcp-kipris
```

## 환경 설정

이 패키지를 사용하기 위해서는 다음 환경 변수 설정이 필요합니다:

```bash
KIPRIS_API_KEY=your_api_key_here
```

API 키는 [특허정보 API Plus](http://plus.kipris.or.kr)에서 회원 가입 후 발급받을 수 있습니다.

## 기능

이 패키지는 국내 특허와 해외 특허 검색을 지원합니다.

### 국내 특허 검색 (Korean Patent Search)

- **키워드 검색**

  - `patent_keyword_search_tool`: 키워드를 통한 특허 검색
  - `patent_search_tool`: 상세 검색 조건을 통한 특허 검색
- **번호 기반 검색**

  - `application_number_search_tool`: 출원번호로 검색
  - `registration_number_search_tool`: 등록번호로 검색
  - `publication_number_search_tool`: 공개번호로 검색
  - `open_number_search_tool`: 공고번호로 검색
- **출원인/권리자 검색**

  - `applicant_search_tool`: 출원인 기준 검색
  - `righter_search_tool`: 권리자 기준 검색
- **상세 정보 조회**

  - `patent_detail_search_tool`: 특허 상세 정보 조회
  - `patent_summary_search_tool`: 특허 요약 정보 조회

### 해외 특허 검색 (Foreign Patent Search)

- **일반 검색**

  - `free_search_tool`: 자유 텍스트 검색
  - `applicant_search_tool`: 출원인 기준 검색
- **번호 기반 검색**

  - `application_number_search_tool`: 출원번호로 검색
  - `international_application_number_search_tool`: 국제출원번호로 검색
  - `international_open_number_search_tool`: 국제공개번호로 검색

## 사용 예시

```python
from mcp_kipris.kipris.tools.korean import PatentKeywordSearchTool

# 키워드 검색 도구 초기화
search_tool = PatentKeywordSearchTool()

# 검색 실행
result = search_tool.run_tool({
    "search_word": "인공지능",  # 검색어
    "patent": True,            # 특허 포함
    "utility": True,           # 실용신안 포함
    "docs_count": 10          # 검색 결과 수
})

# 결과 출력 (pandas DataFrame 형태)
print(result)
```

## 지원하는 국가 코드

해외 특허 검색 시 사용 가능한 국가 코드:

- `US`: 미국
- `EP`: 유럽
- `WO`: PCT
- `JP`: 일본
- `PJ`: 일본영문초록
- `CP`: 중국
- `CN`: 중국특허영문초록
- `TW`: 대만영문초록
- `RU`: 러시아
- `CO`: 콜롬비아
- `SE`: 스웨덴
- `ES`: 스페인
- `IL`: 이스라엘

## 의존성

- Python >= 3.12
- pandas >= 2.2.3
- requests >= 2.32.3
- mcp[cli] >= 1.5.0

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 기여하기

버그 리포트나 기능 제안은 GitHub 이슈를 통해 제출해 주세요.

## 주의사항

1. 이 패키지를 사용하기 위해서는 MCP Server가 필요합니다.
2. Kipris Plus API 키가 필요합니다:
   - [특허정보 API Plus](http://plus.kipris.or.kr)에서 회원 가입
   - 로그인 후 API 키 발급
   - 환경 변수 `KIPRIS_API_KEY`에 발급받은 키 설정
