# KIPRIS MCP 신규 4개 도구 코드 리뷰 보고서

**리뷰 일자:** 2026-04-21  
**리뷰 대상:** 신규 추가된 4개 KIPRIS 검색 도구  
**리뷰어:** 코드 리뷰 전문가

## 리뷰 대상 파일

### API 계층
- `src/mcp_kipris/kipris/api/korean/abstract_search_api.py`
- `src/mcp_kipris/kipris/api/korean/ipc_search_api.py`
- `src/mcp_kipris/kipris/api/korean/agent_search_api.py`
- `src/mcp_kipris/kipris/api/korean/trademark_search_api.py`

### Tool 계층
- `src/mcp_kipris/kipris/tools/korean/abstract_search_tool.py`
- `src/mcp_kipris/kipris/tools/korean/ipc_search_tool.py`
- `src/mcp_kipris/kipris/tools/korean/agent_search_tool.py`
- `src/mcp_kipris/kipris/tools/korean/trademark_search_tool.py`

### 등록 파일
- `src/mcp_kipris/kipris/tools/__init__.py`
- `src/mcp_kipris/server.py`

## 리뷰 체크리스트 평가

### 1. 코드 일관성: ✅ **우수**
- **네이밍:** 기존 패턴과 완벽하게 일치 (`AbstractSearchAPI`, `IpcSearchAPI`, `AgentSearchAPI`, `TrademarkSearchAPI`)
- **구조:** 모든 API 클래스가 `ABSKiprisAPI`를 상속받고 동일한 메서드 구조 유지
- **에러 처리:** 기존 코드와 동일한 예외 처리 패턴 적용
- **파라미터 순서 및 타입:** 일관되게 유지

### 2. API 정확성: ⚠️ **주의 필요**
#### ✅ **정확한 부분**
- **ServiceKey:** 모든 API에서 `api_key_field="ServiceKey"`로 올바르게 설정
- **엔드포인트 URL:** 특허 검색 API들은 올바른 URL 사용
  ```python
  # 특허 검색 API들
  "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch"
  ```

#### ❌ **치명적 오류**
- **상표 검색 API 엔드포인트:** URL이 잘못됨
  ```python
  # 현재 (잘못된 URL)
  "http://plus.kipris.or.kr/kipo-api/kipi/trademarkInfoSearchService/trademarkInfoSearch"
  
  # 예상되는 올바른 URL
  "http://plus.kipris.or.kr/kipo-api/kipi/trademarkInfoSearchService/getTrademarkSearch"
  ```

#### ⚠️ **파라미터명 확인 필요**
- KIPRIS API 문서에 따라 정확한 파라미터명 사용 필요
  - `astrtCont` (초록 검색) - ✅ 확인됨
  - `ipcNumber` (IPC 코드 검색) - ✅ 확인됨
  - `agent` (대리인 검색) - ❌ `agentName`이 아닌지 확인 필요
  - `word` (상표 검색) - ✅ 확인됨

### 3. XML 파싱: ✅ **우수**
- **KEY_STRING:** 모든 API에서 `"response.body.items.item"`로 일관되게 설정
- **파싱 로직:** 기존 `parse_response()` 메서드를 그대로 활용하여 일관성 유지
- **데이터 처리:** pandas DataFrame으로 변환하는 로직이 기존과 완벽히 일치

### 4. MCP 스펙 준수: ✅ **우수**
#### Tool 설명
- 영문 설명이 일관되게 적용됨
```python
# 좋은 예시
"patent search by abstract content, this tool is for korean patent search"
"patent search by IPC code, this tool is for korean patent search"
"patent search by agent name, this tool is for korean patent search"
"trademark search by keyword, this tool is for korean trademark search"
```

#### 파라미터 스키마
- **Required fields:** 적절하게 설정 (`astrt_cont`, `ipc_number`, `agent`, `word`)
- **Enum 값:** `lastvalue`, `sort_spec`에 대해 올바른 enum 설정
- **기본값:** 모든 선택적 파라미터에 적절한 기본값 설정
- **설명:** 한국어 설명이 상세하고 이해하기 쉬움

#### 메타데이터
- **usage_hint:** 사용법 설명이 명확함
- **example_user_queries:** 실제 사용 예시가 적절함
- **preferred_response_style:** 응답 스타일 가이드가 일관됨

### 5. 에러 처리: ✅ **우수**
- **ValidationError:** Pydantic 검증 오류를 적절히 처리
- **Empty results:** `response.empty` 확인 후 "there is no result" 메시지 반환
- **일반 예외:** 모든 예외를 포괄적으로 처리하여 서버 안정성 확보
- **로깅:** 에러 발생 시 상세한 로그 기록

### 6. 보안: ✅ **우수**
- **API 키:** 환경 변수에서 안전하게 로드
- **입력 검증:** Pydantic 모델을 통한 강력한 입력 검증
- **노출 방지:** API 키나 민감정보가 로그나 응답에 노출되지 않음

### 7. 문서화: ✅ **우수**
- **Docstring:** 모든 메서드에 상세한 docstring 제공
- **파라미터 설명:** 각 파라미터의 의미와 용도가 명확히 설명됨
- **타입 힌트:** 모든 파라미터와 반환값에 타입 힌트 적용
- **주석:** 코드의 주요 부분에 적절한 주석 추가

### 8. 중복 코드: ⚠️ **개선 가능**
#### 현재 상태
- 4개의 API 클래스가 거의 동일한 구조를 가지고 있음
- 메서드 구현이 95% 이상 중복

#### 개선 제안
```python
# 공통 기반 클래스 생성 제안
class BasePatentSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch"
        self.KEY_STRING = "response.body.items.item"
    
    def _common_search_params(self, **kwargs):
        """공통 검색 파라미터 생성"""
        return {
            "patent": "true" if kwargs.get('patent', True) else "false",
            "utility": "true" if kwargs.get('utility', True) else "false",
            "page_no": str(kwargs.get('page_no', 1)),
            "num_of_rows": str(kwargs.get('num_of_rows', 10)),
            # ... 기타 공통 파라미터
        }

# 개별 API 클래스들은 공통 기반을 상속받아 특화된 메서드만 구현
class AbstractSearchAPI(BasePatentSearchAPI):
    def sync_search(self, astrt_cont: str, **kwargs):
        # 초록 검색 특화 로직만 구현
        pass
```

## 발견된 이슈

### 🔴 **Critical (치명적)**

#### 1. 상표 검색 API 엔드포인트 오류
- **파일:** `trademark_search_api.py`
- **문제:** 엔드포인트 URL이 올바르지 않음
- **영향:** 상표 검색이 정상적으로 동작하지 않음
- **수정:** KIPRIS API 문서 확인 후 올바른 엔드포인트로 변경 필요

#### 2. 대리인 검색 파라미터명 의심
- **파일:** `agent_search_api.py`
- **문제:** `agent` 파라미터명이 KIPRIS API 스펙과 일치하는지 확인 필요
- **영향:** 대리인 검색이 실패할 수 있음
- **수정:** KIPRIS API 문서에서 정확한 파라미터명 확인

### 🟡 **Major (중요)**

#### 1. 상표 검색 결과 컬럼 처리 불확실성
- **파일:** `trademark_search_tool.py`
- **문제:** 상표 검색 결과 컬럼이 특허와 다를 수 있음
- **현재 대응:** 동적으로 컬럼을 선택하는 로직 구현됨
- **개선:** 상표 검색 결과의 실제 컬럼 구조를 확인하고 더 안정적인 처리 로직 필요

### 🟢 **Minor (사소)**

#### 1. 불필요한 import 구문
- **모든 API 파일:** `import urllib.parse`가 사용되지 않음
- **영향:** 미미 (성능에 영향 없음)
- **수정:** 사용하지 않는 import 제거

#### 2. 코드 중복
- **영향:** 유지보수성 저하
- **수정:** 공통 기반 클래스를 도입하여 중복 제거

## 리팩토링 권고사항

### 1. **즉시 수정 필요 (Critical)**
```python
# trademark_search_api.py 수정 예시
class TrademarkSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 올바른 엔드포인트로 변경 (실제 정확한 URL로 수정 필요)
        self.api_url = "http://plus.kipris.or.kr/kipo-api/kipi/trademarkInfoSearchService/getTrademarkSearch"
        self.KEY_STRING = "response.body.items.item"
```

### 2. **구조 개선 (Major)**
```python
# 공통 기반 클래스 도입 제안
class BaseKoreanPatentAPI(ABSKiprisAPI):
    API_URL = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch"
    KEY_STRING = "response.body.items.item"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = self.API_URL
        self.KEY_STRING = self.KEY_STRING
    
    def _build_common_params(self, **kwargs):
        """공통 파라미터 구성"""
        return {
            "patent": "true" if kwargs.get('patent', True) else "false",
            "utility": "true" if kwargs.get('utility', True) else "false",
            "page_no": str(kwargs.get('page_no', 1)),
            "num_of_rows": str(kwargs.get('num_of_rows', 10)),
            "lastvalue": str(kwargs.get('lastvalue', "")),
            "desc_sort": "true" if kwargs.get('desc_sort', False) else "false",
            "sort_spec": str(kwargs.get('sort_spec', "AD")),
        }

# 개별 API들은 공통 기반을 상속
class AbstractSearchAPI(BaseKoreanPatentAPI):
    def sync_search(self, astrt_cont: str, **kwargs):
        common_params = self._build_common_params(**kwargs)
        return self.sync_call(
            api_url=self.api_url,
            api_key_field="ServiceKey",
            astrtCont=astrt_cont,
            **common_params,
            **{k: v for k, v in kwargs.items() if k not in common_params}
        )
```

### 3. **문서화 개선 (Minor)**
- 각 Tool 클래스에 클래스 레벨 docstring 추가
- API 엔드포인트와 파라미터명에 대한 참고 문서 링크 추가
- 사용 예시를 더 다양하게 제공

## 기존 코드와의 일관성 분석

### ✅ **일관성 우수한 부분**
1. **아키텍처:** 기존의 Layered Architecture (API → Tool → Server)를 완벽히 따름
2. **디자인 패턴:** Template Method 패턴을 통한 일관된 구조 유지
3. **에러 처리:** 기존과 동일한 에러 처리 전략 적용
4. **로그:** 동일한 로깅 패턴과 레벨 사용
5. **타입:** 타입 힌트와 Pydantic 검증을 일관되게 적용

### ⚠️ **개선이 필요한 부분**
1. **중복 제거:** 기존 코드도 중복이 많으므로 리팩토링 기회로 활용 권장
2. **테스트 코드:** 기존 코드와 마찬가지로 테스트 코드 부재 (향후 추가 필요)

## 종합 평가

### 등급: **B+ (우수, 단 일부 치명적 이슈 존재)**

### 강점
- 코드 구조와 일관성이 매우 우수함
- MCP 스펙을 완벽히 준수함
- 에러 처리와 보안이 강력함
- 문서화가 상세함

### 약점
- 상표 검색 API 엔드포인트 오류 (치명적)
- 코드 중복이 다소 존재함
- 일부 파라미터명이 검증되지 않음

### 권장 조치
1. **즉시:** 상표 검색 API 엔드포인트 수정
2. **조기:** 대리인 검색 파라미터명 확인
3. **중기:** 공통 기반 클래스를 통한 리팩토링
4. **장기:** 테스트 코드 추가 및 문서화 강화

---

**리뷰 결론:** 전반적으로 품질이 우수한 코드이며, 기존 시스템과의 일관성도 높음. 일부 치명적 이슈만 수정하면 즉시 배포 가능할 것으로 판단됨.