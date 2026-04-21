import typing as t
import urllib.parse
from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value

logger = getLogger("mcp-kipris")


def _select_columns(df: pd.DataFrame, expected_cols: list[str]) -> pd.DataFrame:
    """Safely select available columns, avoiding KeyError on unexpected schema."""
    if df.empty:
        return df
    available = [c for c in expected_cols if c in df.columns]
    if not available:
        logger.warning(f"Unexpected columns in response: {list(df.columns)}")
        return df
    return df[available]


FOREIGN_APPLICANT_COLS = ["applicationNo", "applicationDate", "inventionName", "applicant"]


class ForeignPatentApplicantSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/ForeignPatentAdvencedSearchService/applicantSearch"
        self.KEY_STRING = "response.body.items.searchResult"

    async def async_search(
        self,
        applicant: str,
        current_page: int = 1,
        sort_field: str = "AD",
        sort_state: bool = True,
        collection_values: str = "US",
    ) -> pd.DataFrame:
        """해외 특허 출원인 검색

        Args:
            applicant (str): 출원인 이름
            current_page (int, optional): 페이지 번호. Defaults to 1.
            sort_field (str, optional): 정렬 기준. Defaults to "AD".
                (AD-출원일자, PD-공고일자, GD-등록일자, OPD-공개일자, FD-국제출원일자, FOD-국제공개일자, RD-우선권주장일자)
            sort_state (bool, optional): 내림차순 정렬. Defaults to True. other wise False
            collection_values (str, optional): 검색 대상 국가. Defaults to "US".
                (미국-US, 유럽-EP, PCT-WO, 일본-JP, 일본영문초록-PJ, 중국-CP, 중국특허영문초록-CN, 대만영문초록-TW, 러시아-RU, 콜롬비아-CO, 스웨덴-SE, 스페인-ES, 이스라엘-IL)
                ※다중 국가 선택 불가

        Returns:
            pd.DataFrame: 검색 결과
        """
        logger.info(f"applicant: {applicant}")

        response = await self.async_call(
            api_url=self.api_url,
            api_key_field="accessKey",
            applicant=applicant,
            current_page=str(current_page),
            sort_field=str(sort_field),
            sort_state="true" if sort_state else "false",
            collection_values=str(collection_values),
        )
        df = self.parse_response(response)
        return _select_columns(df, FOREIGN_APPLICANT_COLS)

    def sync_search(
        self,
        applicant: str,
        current_page: int = 1,
        sort_field: str = "AD",
        sort_state: bool = True,
        collection_values: str = "US",
    ) -> pd.DataFrame:
        """해외 특허 출원인 검색 (동기)

        Args:
            applicant (str): 출원인 이름
            current_page (int, optional): 페이지 번호. Defaults to 1.
            sort_field (str, optional): 정렬 기준. Defaults to "AD".
                (AD-출원일자, PD-공고일자, GD-등록일자, OPD-공개일자, FD-국제출원일자, FOD-국제공개일자, RD-우선권주장일자)
            sort_state (bool, optional): 내림차순 정렬. Defaults to True. other wise False
            collection_values (str, optional): 검색 대상 국가. Defaults to "US".
                (미국-US, 유럽-EP, PCT-WO, 일본-JP, 일본영문초록-PJ, 중국-CP, 중국특허영문초록-CN, 대만영문초록-TW, 러시아-RU, 콜롬비아-CO, 스웨덴-SE, 스페인-ES, 이스라엘-IL)
                ※다중 국가 선택 불가

        Returns:
            pd.DataFrame: 검색 결과
        """
        logger.info(f"applicant: {applicant}")

        response = self.sync_call(
            api_url=self.api_url,
            api_key_field="accessKey",
            applicant=applicant,
            current_page=str(current_page),
            sort_field=str(sort_field),
            sort_state="true" if sort_state else "false",
            collection_values=str(collection_values),
        )
        df = self.parse_response(response)
        return _select_columns(df, FOREIGN_APPLICANT_COLS)
