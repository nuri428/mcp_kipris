#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
특허 검색 테스트 스크립트

이 스크립트는 mcp_kipris 라이브러리를 사용하여
특허 검색 API를 테스트하는 예제입니다.
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# 모듈 경로 추가 (프로젝트 루트 기준으로 설정)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# .env 파일에서 환경 변수 로드
load_dotenv(project_root / "src" / ".env")

# 특허 검색 도구 import
from mcp_kipris.kipris.tools.korean.patent_search_tool import PatentSearchTool


def main():
    # 검색 도구 인스턴스화
    tool = PatentSearchTool()

    # 테스트할 출원번호
    application_number = "1020200042879"

    print(f"출원번호 {application_number}로 특허 검색 중...")

    # 동기 방식 검색
    result = tool.run_tool(
        {
            "application_number": application_number,
        }
    )

    # 결과 출력
    print_results(result)

    # 비동기 방식 테스트 (asyncio.run으로 실행)
    print("\n비동기 방식으로 동일한 검색 수행 중...")

    import asyncio

    async def test_async():
        return await tool.run_tool_async(
            {
                "application_number": application_number,
            }
        )

    async_result = asyncio.run(test_async())
    print_results(async_result)


def print_results(result):
    """결과를 보기 좋게 출력하는 함수"""
    if isinstance(result, pd.DataFrame):
        print("\n특허 검색 결과:")
        print(result.to_string(index=False))
    elif isinstance(result, list):
        for i, item in enumerate(result, 1):
            if isinstance(item, dict):
                print(f"\n[검색 결과 {i}]")
                for key, value in item.items():
                    print(f"{key}: {value}")
            else:
                from mcp.types import TextContent

                if isinstance(item, TextContent):
                    print(f"\n[검색 결과 {i}]")
                    try:
                        data = json.loads(item.text)
                        if isinstance(data, list):
                            for j, patent in enumerate(data, 1):
                                print(f"\n[특허 {i}.{j}]")
                                # 중요 필드만 출력
                                important_fields = ["출원번호", "출원일자", "발명의명칭", "출원인", "요약"]
                                for k, v in patent.items():
                                    if k in important_fields:
                                        if k == "요약":
                                            print(f"{k}: {v[:100]}..." if len(v) > 100 else f"{k}: {v}")
                                        else:
                                            print(f"{k}: {v}")
                        else:
                            print(data)
                    except Exception as e:
                        print(f"JSON 파싱 오류: {e}")
                        print(item.text)
                else:
                    print(f"Unknown type: {type(item)}")
                    print(item)
    else:
        print("검색 결과:", result)


if __name__ == "__main__":
    main()
