#!/usr/bin/env python3
"""
KIPRIS API 응답 컬럼명 확인 스크립트
"""

import asyncio
import os
import sys
from pathlib import Path

# 소스 디렉토리를 Python 경로에 추가
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from mcp_kipris.kipris.api.korean.abstract_search_api import AbstractSearchAPI
from mcp_kipris.kipris.api.korean.ipc_search_api import IpcSearchAPI

async def debug_abstract_search():
    """초록 검색 API 응답 컬럼명 확인"""
    print("🔍 Abstract Search API 응답 컬럼명 확인")
    print("=" * 50)
    
    # API 키 설정
    api_key = "xnW756/wS0kIQ4IKsiRBrtMJrvMBd/vXogNu3VAn8wQ="
    os.environ['KIPRIS_API_KEY'] = api_key
    
    # API 인스턴스 생성
    api = AbstractSearchAPI(api_key=api_key)
    
    try:
        # API 호출
        response = await api.async_search(
            astrt_cont="인공지능",
            page_no=1,
            num_of_rows=5
        )
        
        if response is not None and not response.empty:
            print(f"✅ 응답 받음: {len(response)}건")
            print(f"📊 컬럼명 목록:")
            for i, col in enumerate(response.columns, 1):
                print(f"   {i:2d}. {col}")
            
            # 첫 번째 행의 데이터
            print(f"\n📋 첫 번째 행 데이터:")
            first_row = response.iloc[0]
            for col in response.columns:
                value = first_row[col]
                if pd.notna(value) and str(value).strip():
                    print(f"   {col}: {value}")
                    
        else:
            print("❌ 응답이 없거나 비어있음")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

async def debug_ipc_search():
    """IPC 검색 API 응답 컬럼명 확인"""
    print("\n🔍 IPC Search API 응답 컬럼명 확인")
    print("=" * 50)
    
    # API 키 설정
    api_key = "xnW756/wS0kIQ4IKsiRBrtMJrvMBd/vXogNu3VAn8wQ="
    os.environ['KIPRIS_API_KEY'] = api_key
    
    # API 인스턴스 생성
    api = IpcSearchAPI(api_key=api_key)
    
    try:
        # API 호출
        response = await api.async_search(
            ipc_number="G06F",
            page_no=1,
            num_of_rows=5
        )
        
        if response is not None and not response.empty:
            print(f"✅ 응답 받음: {len(response)}건")
            print(f"📊 컬럼명 목록:")
            for i, col in enumerate(response.columns, 1):
                print(f"   {i:2d}. {col}")
            
            # 첫 번째 행의 데이터
            print(f"\n📋 첫 번째 행 데이터:")
            first_row = response.iloc[0]
            for col in response.columns:
                value = first_row[col]
                if pd.notna(value) and str(value).strip():
                    print(f"   {col}: {value}")
                    
        else:
            print("❌ 응답이 없거나 비어있음")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    import pandas as pd
    asyncio.run(debug_abstract_search())
    asyncio.run(debug_ipc_search())