#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
출원번호 검색 테스트 스크립트

이 스크립트는 mcp_kipris 라이브러리를 사용하여
특정 출원번호 패턴으로 특허를 검색하는 예제입니다.
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
from mcp_kipris.kipris.tools.korean.application_number_search_tool import PatentApplicationNumberSearchTool


def main():
    # 검색 도구 인스턴스화
    tool = PatentApplicationNumberSearchTool()

    # 검색할 출원번호 패턴 (2020년 출원, 일부만 지정)
    application_number = "102020004"

    print(f"출원번호 패턴 '{application_number}'로 특허 검색 중...")

    # 동기 방식 검색
    result = tool.run_tool(
        {
            "application_number": application_number,
            "docs_count": 3,  # 검색 결과 수: 3개
            "desc_sort": True,  # 내림차순 정렬 (최신순)
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
                "docs_count": 3,
                "desc_sort": True,
            }
        )

    async_result = asyncio.run(test_async())
    print_results(async_result)


def print_results(result):
    """결과를 보기 좋게 출력하는 함수"""
    if isinstance(result, pd.DataFrame):
        print("\n출원번호 검색 결과:")
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
                                for k, v in patent.items():
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
