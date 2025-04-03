#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
권리자 검색 API 디버깅 스크립트
"""

import os
import sys
from pathlib import Path

# 모듈 경로 추가 (프로젝트 루트 기준으로 설정)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# .env 파일에서 환경 변수 로드
from dotenv import load_dotenv

load_dotenv(project_root / "src" / ".env")

# API 로거 설정
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp-kipris")
logger.setLevel(logging.DEBUG)

# API 직접 호출
from mcp_kipris.kipris.api.korean.righter_search_api import PatentRighterSearchAPI

api_key = os.getenv("KIPRIS_API_KEY")
if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")

# API 인스턴스 생성
api = PatentRighterSearchAPI(api_key=api_key)

# 권리자 검색 수행
print("삼성전자 권리자 검색 시작...")
df = api.sync_search(rightHoler="삼성전자", docs_start=1, docs_count=3, desc_sort=True)

# 결과 확인
if df.empty:
    print("검색 결과가 없습니다.")
else:
    print(f"총 {len(df)}개의 특허 발견")
    print("\n데이터프레임 정보:")
    print(df.info())
    print("\n데이터프레임 열:")
    print(df.columns.tolist())
    print("\n첫 번째 행:")
    first_row = df.iloc[0].to_dict()
    for k, v in first_row.items():
        print(f"{k}: {v}")

    # JSON 파일로 저장
    df.to_json("debug_righter_search_result.json", orient="records", indent=2, force_ascii=False)
    print("\n결과가 debug_righter_search_result.json 파일에 저장되었습니다.")
