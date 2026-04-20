#!/usr/bin/env python3
"""
추가 QA 테스트 - 다른 검색어로 테스트
"""

import asyncio
import os
import sys
from pathlib import Path

# 소스 디렉토리를 Python 경로에 추가
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from mcp_kipris.kipris.tools.korean.agent_search_tool import AgentSearchTool
from mcp_kipris.kipris.tools.korean.trademark_search_tool import TrademarkSearchTool

async def test_agent_search():
    """대리인 검색 - 다른 검색어로 테스트"""
    print("🔍 Agent Search - 추가 테스트")
    print("=" * 40)
    
    # API 키 설정
    api_key = "xnW756/wS0kIQ4IKsiRBrtMJrvMBd/vXogNu3VAn8wQ="
    os.environ['KIPRIS_API_KEY'] = api_key
    
    # 도구 인스턴스 생성
    tool = AgentSearchTool()
    
    # 다양한 검색어로 테스트
    test_keywords = ["김앤김", "태평양", "세종", "변호사", "특허"]
    
    for keyword in test_keywords:
        print(f"\n   테스트: {keyword}")
        try:
            result = await tool.run_tool_async({"agent": keyword})
            if result and len(result) > 0:
                content = result[0].text
                if "there is no result" in content:
                    print(f"      ❌ 결과 없음")
                else:
                    print(f"      ✅ 결과 있음: {len(content)}자")
                    if len(content) > 100:
                        print(f"      📄 {content[:100]}...")
            else:
                print(f"      ❌ 응답 없음")
        except Exception as e:
            print(f"      ❌ 오류: {e}")

async def test_trademark_search():
    """상표 검색 - 파라미터 조정 테스트"""
    print("\n🔍 Trademark Search - 파라미터 테스트")
    print("=" * 40)
    
    # API 키 설정
    api_key = "xnW756/wS0kIQ4IKsiRBrtMJrvMBd/vXogNu3VAn8wQ="
    os.environ['KIPRIS_API_KEY'] = api_key
    
    # 도구 인스턴스 생성
    tool = TrademarkSearchTool()
    
    # 기본 파라미터만 테스트
    try:
        print(f"\n   테스트: 삼성 (기본 파라미터)")
        result = await tool.run_tool_async({"word": "삼성"})
        if result and len(result) > 0:
            content = result[0].text
            print(f"      응답: {content}")
        else:
            print(f"      ❌ 응답 없음")
    except Exception as e:
        print(f"      ❌ 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_search())
    asyncio.run(test_trademark_search())