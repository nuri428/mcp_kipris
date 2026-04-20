#!/usr/bin/env python3
"""
KIPRIS MCP 신규 4개 도구 QA 테스트 스크립트
- abstract_search (초록 검색)
- ipc_search (IPC 코드 검색)  
- agent_search (대리인 검색)
- trademark_search (상표 검색)
"""

import json
import os
import sys
from pathlib import Path

# 소스 디렉토리를 Python 경로에 추가
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from mcp_kipris.kipris.tools.korean.abstract_search_tool import AbstractSearchTool
from mcp_kipris.kipris.tools.korean.ipc_search_tool import IpcSearchTool
from mcp_kipris.kipris.tools.korean.agent_search_tool import AgentSearchTool
from mcp_kipris.kipris.tools.korean.trademark_search_tool import TrademarkSearchTool

# API 키 로드
def load_api_key():
    """시크릿 파일에서 API 키 로드"""
    try:
        secrets_file = os.path.expanduser('~/.openclaw/secrets.json')
        with open(secrets_file, 'r', encoding='utf-8') as f:
            secrets = json.load(f)
            return secrets.get('KIPRIS_API_KEY')
    except Exception as e:
        print(f"❌ API 키 로드 실패: {e}")
        return None

# 테스트 결과 클래스
class TestResult:
    def __init__(self, tool_name, status, details="", issues=None):
        self.tool_name = tool_name
        self.status = status  # PASS, FAIL, ERROR
        self.details = details
        self.issues = issues or []
    
    def to_dict(self):
        return {
            "tool": self.tool_name,
            "status": self.status,
            "details": self.details,
            "issues": self.issues
        }

# 테스트 실행 함수
async def test_tool(tool_class, tool_name, test_params, api_key):
    """단일 도구 테스트 실행"""
    print(f"\n🧪 테스트 시작: {tool_name}")
    print(f"   파라미터: {test_params}")
    
    try:
        # 환경변수에 API 키 설정
        os.environ['KIPRIS_API_KEY'] = api_key
        
        # 도구 인스턴스 생성
        tool = tool_class()
        
        # 테스트 실행
        result = await tool.run_tool_async(test_params)
        
        # 결과 검증
        if isinstance(result, list) and len(result) > 0:
            first_content = result[0]
            if hasattr(first_content, 'text'):
                text_content = first_content.text
                print(f"   ✅ 성공: 응답 받음")
                print(f"   응답 내용 (200자): {text_content[:200]}...")
                
                # 응답 내용 분석
                if "there is no result" in text_content:
                    return TestResult(
                        tool_name,
                        "FAIL",
                        "검색 결과가 없음",
                        ["빈 결과 반환"]
                    )
                elif "오류" in text_content or "입력값 검증 오류" in text_content:
                    return TestResult(
                        tool_name,
                        "ERROR",
                        f"응답 오류: {text_content}",
                        [f"응답 오류: {text_content[:100]}"]
                    )
                else:
                    # 정상 응답인지 확인 (마크다운 테이블 형식인지)
                    if "|" in text_content and ("applicationNumber" in text_content or "ApplicationNumber" in text_content):
                        return TestResult(
                            tool_name,
                            "PASS",
                            f"정상 작동: 테이블 형식 응답 반환"
                        )
                    else:
                        return TestResult(
                            tool_name,
                            "FAIL",
                            f"예상치 못한 응답 형식: {text_content[:100]}",
                            ["응답 형식 오류"]
                        )
            else:
                return TestResult(
                    tool_name,
                    "ERROR",
                    "TextContent 형식이 아님",
                    ["잘못된 응답 형식"]
                )
        else:
            return TestResult(
                tool_name,
                "ERROR",
                "빈 응답 또는 형식 오류",
                ["응답 형식 오류"]
            )
            
    except Exception as e:
        print(f"   ❌ 예외 발생: {str(e)}")
        return TestResult(
            tool_name,
            "ERROR",
            f"예외 발생: {str(e)}",
            [f"예외: {str(e)}"]
        )

# 메인 테스트 함수
async def run_all_tests():
    """모든 도구 테스트 실행"""
    print("🚀 KIPRIS MCP QA 테스트 시작")
    print("=" * 50)
    
    # API 키 로드
    api_key = load_api_key()
    if not api_key:
        print("❌ API 키를 로드할 수 없습니다.")
        return
    
    print(f"🔑 API 키 로드 성공 (길이: {len(api_key)})")
    
    # 테스트 설정
    test_cases = [
        (AbstractSearchTool, "abstract_search", {"astrt_cont": "인공지능"}),
        (IpcSearchTool, "ipc_search", {"ipc_number": "G06F"}),
        (AgentSearchTool, "agent_search", {"agent": "태평양"}),  # 결과가 있는 검색어로 변경
        (TrademarkSearchTool, "trademark_search", {"word": "삼성"}),
    ]
    
    # 테스트 실행
    results = []
    for tool_class, tool_name, params in test_cases:
        result = await test_tool(tool_class, tool_name, params, api_key)
        results.append(result)
        print(f"   결과: {result.status} - {result.details}")
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    for result in results:
        status_icon = "✅" if result.status == "PASS" else "❌"
        print(f"{status_icon} {result.tool_name}: {result.status}")
        if result.issues:
            for issue in result.issues:
                print(f"   ⚠️  {issue}")
    
    # 보고서 생성
    generate_report(results)
    
    # 전체 결과
    passed = sum(1 for r in results if r.status == "PASS")
    total = len(results)
    
    print(f"\n🎯 최종 결과: {passed}/{total} 통과")
    return results

def generate_report(results):
    """QA 보고서 생성"""
    report_path = Path(__file__).parent / "docs" / "qa-report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# KIPRIS MCP QA 테스트 보고서\n\n")
        f.write(f"**테스트 일시:** {Path(__file__).stat().st_mtime}\n\n")
        
        # 요약
        passed = sum(1 for r in results if r.status == "PASS")
        total = len(results)
        f.write("## 요약\n\n")
        f.write(f"- **전체 도구:** {total}개\n")
        f.write(f"- **통과:** {passed}개\n")
        f.write(f"- **실패/오류:** {total - passed}개\n\n")
        
        # 각 도구별 결과
        f.write("## 도구별 테스트 결과\n\n")
        for result in results:
            f.write(f"### {result.tool_name}\n\n")
            f.write(f"- **상태:** {result.status}\n")
            f.write(f"- **설명:** {result.details}\n")
            if result.issues:
                f.write("- **이슈:**\n")
                for issue in result.issues:
                    f.write(f"  - {issue}\n")
            f.write("\n")
        
        # 발견된 버그/이슈 목록
        all_issues = []
        for result in results:
            if result.issues:
                all_issues.extend(result.issues)
        
        f.write("## 발견된 버그/이슈 목록\n\n")
        if all_issues:
            for i, issue in enumerate(all_issues, 1):
                f.write(f"{i}. {issue}\n")
        else:
            f.write("발견된 이슈가 없습니다.\n")
        f.write("\n")
        
        # 개선 권고사항
        f.write("## 개선 권고사항\n\n")
        f.write("1. **에러 처리 강화**: 모든 도구에서 일관된 에러 메시지 형식 제공\n")
        f.write("2. **입력 검증**: 파라미터 유효성 검사 로직 추가\n")
        f.write("3. **결과 포맷 표준화**: 모든 도구에서 동일한 필드 구조 반환\n")
        f.write("4. **테스트 커버리지 확대**: 경계값 테스트 및 예외 상황 테스트 추가\n")
        f.write("5. **문서화**: 각 도구의 파라미터와 반환값에 대한 상세 문서 제공\n")
    
    print(f"\n📄 보고서 생성 완료: {report_path}")

if __name__ == "__main__":
    import asyncio
    
    # 테스트 실행
    results = asyncio.run(run_all_tests())