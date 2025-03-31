#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
에코프로비엠 특허 검색 간단 테스트 스크립트

이 스크립트는 KIPRIS API를 직접 호출하여
에코프로비엠이 출원한 최신 특허 30개를 검색하는 예제입니다.
"""

import json
import os
import sys
import time
import urllib.parse
from pathlib import Path

import pandas as pd
import requests
import xmltodict
from dotenv import load_dotenv

# 모듈 경로 추가 (프로젝트 루트 기준으로 설정)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# .env 파일에서 환경 변수 로드
load_dotenv(project_root / "src" / ".env")

# API 키 가져오기
api_key = os.getenv("KIPRIS_API_KEY")
if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")


def get_nested_key_value(dictionary, nested_key, sep=".", default_value=None):
    """계층적 딕셔너리에서 중첩된 키의 값을 가져오는 함수"""
    if dictionary is None:
        return default_value

    try:
        current = dictionary
        for keys in nested_key.split(sep):
            if current and keys in current:
                current = current[keys]
            else:
                return default_value

        return current if current is not None else default_value
    except Exception as e:
        print(f"키 추출 오류: {e}")
        return default_value


def search_applicant(applicant, docs_count=30, desc_sort=True):
    """출원인 기반 특허 검색 함수"""
    print(f"출원인 '{applicant}' 특허 {docs_count}개 검색 중...")
    print("이 작업은 시간이 오래 걸릴 수 있습니다. (최대 10분)")

    start_time = time.time()

    # API URL 및 파라미터 설정
    base_url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/applicantNameSearchInfo"
    encoded_applicant = urllib.parse.quote(applicant)

    params = {
        "applicant": encoded_applicant,
        "patent": "True",
        "utility": "True",
        "docsStart": "1",
        "docsCount": str(docs_count),
        "sortSpec": "AD",
        "descSort": "true" if desc_sort else "false",
        "accessKey": api_key,
    }

    # URL 구성
    url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    print(f"요청 URL: {url}")

    try:
        # API 호출
        response = requests.get(url, timeout=(60, 600))  # 연결 60초, 응답 600초 타임아웃

        # XML 응답을 JSON으로 변환
        dict_type = xmltodict.parse(response.text)
        json_data = json.loads(json.dumps(dict_type))

        # 응답 헤더 확인
        result_header = get_nested_key_value(json_data, "response.header", default_value="")
        print(f"API 응답 헤더: {result_header}")

        # 특허 정보 추출
        patents = get_nested_key_value(json_data, "response.body.items.PatentUtilityInfo")

        # 결과 처리
        if patents is None:
            print("검색 결과가 없습니다.")
            return None

        # 단일 결과를 리스트로 변환
        if isinstance(patents, dict):
            patents = [patents]

        # 데이터프레임으로 변환
        df = pd.DataFrame(patents)

        # 실행 시간 측정
        elapsed_time = time.time() - start_time
        print(f"\n검색 완료! 소요 시간: {elapsed_time:.2f}초")
        print(f"총 {len(df)}개의 특허 발견")

        return df

    except requests.exceptions.Timeout as e:
        print(f"타임아웃 오류: {e}")
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")

    return None


def main():
    try:
        # 에코프로비엠 특허 검색
        df = search_applicant("에코프로비엠", docs_count=30)

        if df is not None and not df.empty:
            # 결과 출력
            print("\n--- 처음 5개 특허 정보 ---")
            for i, (_, row) in enumerate(df.head(5).iterrows(), 1):
                print(f"\n[특허 {i}]")
                important_fields = ["출원번호", "출원일자", "발명의명칭", "출원인"]
                for field in important_fields:
                    if field in row:
                        print(f"{field}: {row[field]}")

            # 결과 저장
            df.to_csv("ecopro_patents_results.csv", index=False, encoding="utf-8-sig")
            print(f"\n결과가 ecopro_patents_results.csv 파일에 저장되었습니다.")

            # JSON 형식으로도 저장
            df.to_json("ecopro_patents_results.json", orient="records", indent=2, force_ascii=False)
            print(f"결과가 ecopro_patents_results.json 파일에도 저장되었습니다.")
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
