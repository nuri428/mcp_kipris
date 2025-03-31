#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
에코프로비엠 특허 검색 테스트 스크립트

이 스크립트는 mcp_kipris 라이브러리를 사용하여
에코프로비엠이 출원한 최신 특허 30개를 검색하는 예제입니다.
"""

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# 모듈 경로 추가 (프로젝트 루트 기준으로 설정)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# .env 파일에서 환경 변수 로드
load_dotenv(project_root / "src" / ".env")

# 특허 검색 도구 import
from mcp_kipris.kipris.tools.korean.applicant_search_tool import PatentApplicantSearchTool


def main():
    # 검색 도구 인스턴스화
    tool = PatentApplicantSearchTool()

    # 에코프로비엠 특허 검색
    print("에코프로비엠 특허 30개 검색 중...")
    print("이 작업은 시간이 오래 걸릴 수 있습니다. (최대 10분)")

    start_time = time.time()

    # 비동기 함수 실행을 위한 도우미 함수
    import asyncio

    async def search_patents_async():
        result = await tool.run_tool_async(
            {
                "applicant": "에코프로비엠",  # 출원인: 에코프로비엠
                "docs_count": 30,  # 검색 결과 수: 30개
                "desc_sort": True,  # 내림차순 정렬 (최신순)
            }
        )
        return result

    # 비동기 함수 실행
    result = asyncio.run(search_patents_async())

    # 실행 시간 측정
    elapsed_time = time.time() - start_time
    print(f"\n검색 완료! 소요 시간: {elapsed_time:.2f}초")

    # 결과 출력
    print_results(result)

    # 결과 파일로 저장
    save_results(result)


def save_results(result):
    """결과를 파일로 저장하는 함수"""
    try:
        if isinstance(result, list) and len(result) > 0:
            from mcp.types import TextContent

            if isinstance(result[0], TextContent):
                # JSON 파일로 저장
                with open("ecopro_patents_results.json", "w", encoding="utf-8") as f:
                    f.write(result[0].text)
                print(f"\n결과가 ecopro_patents_results.json 파일에 저장되었습니다.")

                # 데이터프레임으로 변환하여 CSV로도 저장
                try:
                    data = json.loads(result[0].text)
                    df = pd.DataFrame(data)
                    df.to_csv("ecopro_patents_results.csv", index=False, encoding="utf-8-sig")
                    print(f"결과가 ecopro_patents_results.csv 파일에도 저장되었습니다.")
                except Exception as e:
                    print(f"CSV 변환 중 오류: {e}")
    except Exception as e:
        print(f"결과 저장 중 오류 발생: {e}")


def print_results(result):
    """결과를 보기 좋게 출력하는 함수"""
    if isinstance(result, pd.DataFrame):
        print("\n에코프로비엠의 최신 특허 30개:")
        print(result.to_string(index=False))
    elif isinstance(result, list):
        for i, item in enumerate(result, 1):
            if isinstance(item, dict):
                print(f"\n[특허 {i}]")
                for key, value in item.items():
                    print(f"{key}: {value}")
            else:
                from mcp.types import TextContent

                if isinstance(item, TextContent):
                    print(f"\n[결과 {i}]")
                    try:
                        data = json.loads(item.text)
                        print(f"\n총 {len(data)}개의 특허 발견")

                        # 처음 5개 특허만 상세 출력
                        for j, patent in enumerate(data[:5], 1):
                            print(f"\n[특허 {j}]")
                            important_fields = ["출원번호", "출원일자", "발명의명칭", "출원인", "등록번호", "등록일자"]
                            for k, v in patent.items():
                                if k in important_fields:
                                    print(f"{k}: {v}")

                        # 나머지는 개수만 표시
                        if len(data) > 5:
                            print(f"\n... 외 {len(data) - 5}개 특허 (파일에서 확인 가능)")

                    except Exception as e:
                        print(f"JSON 파싱 오류: {e}")
                        print(item.text[:500] + "..." if len(item.text) > 500 else item.text)
                else:
                    print(f"Unknown type: {type(item)}")
                    print(item)
    else:
        print("검색 결과:", result)


if __name__ == "__main__":
    main()
