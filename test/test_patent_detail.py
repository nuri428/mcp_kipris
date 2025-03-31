#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
특허 상세 정보 조회 테스트 스크립트

이 스크립트는 mcp_kipris 라이브러리를 사용하여
출원번호로 특허 상세 정보를 조회하는 예제입니다.
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
from mcp_kipris.kipris.tools.korean.patent_detail_search_tool import PatentDetailSearchTool


def main():
    # 검색 도구 인스턴스화
    tool = PatentDetailSearchTool()

    # 특허 출원번호로 상세 정보 조회 (삼성전자의 특허 출원번호)
    # 참고: 실제 존재하는 출원번호로 변경해주세요
    application_number = "1020200040556"  # 예시 출원번호

    print(f"출원번호 '{application_number}'로 특허 상세 정보 조회 중...")
    result = tool.run_tool(
        {
            "application_number": application_number,
        }
    )

    # 결과 출력
    print_results(result)


def print_results(result):
    """결과를 보기 좋게 출력하는 함수"""
    if isinstance(result, pd.DataFrame):
        print("\n특허 상세 정보:")
        print(result.to_string(index=False))
    elif isinstance(result, list):
        for i, item in enumerate(result, 1):
            if isinstance(item, dict):
                print(f"\n[상세 정보 {i}]")
                for key, value in item.items():
                    print(f"{key}: {value}")
            else:
                from mcp.types import TextContent

                if isinstance(item, TextContent):
                    print(f"\n[상세 정보 {i}]")
                    try:
                        data = json.loads(item.text)
                        if isinstance(data, list):
                            for j, patent in enumerate(data, 1):
                                print(f"\n[항목 {i}.{j}]")
                                for k, v in patent.items():
                                    print(f"{k}: {v}")
                        else:
                            for k, v in data.items():
                                print(f"{k}: {v}")
                    except Exception as e:
                        print(f"JSON 파싱 오류: {e}")
                        print(item.text)
                else:
                    print(f"Unknown type: {type(item)}")
                    print(item)
    else:
        print("조회 결과:", result)


if __name__ == "__main__":
    main()
