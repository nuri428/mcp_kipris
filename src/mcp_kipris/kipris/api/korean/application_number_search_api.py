import typing as t
from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value

logger = getLogger("mcp-kipris")


class PatentApplicationNumberSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/applicationNumberSearchInfo"
        self.KEY_STRING = "response.body.items.PatentUtilityInfo"

    def sync_search(
        self,
        application_number: str,
        docs_start: int = 1,
        docs_count: int = 10,
        patent: bool = True,
        utility: bool = True,
        lastvalue: str = "",
        sort_spec: str = "AD",
        desc_sort: bool = False,
    ) -> pd.DataFrame:
        """
        특허 번호 검색

        Args:
            application_number (str): 특허 번호
            docs_start (int): 검색 시작 위치
            docs_count (int): 검색 결과 수
        """
        logger.info(f"application_number: {application_number}")
        response = self.sync_call(
            api_url=self.api_url,
            application_number=application_number,
            docs_start=str(docs_start),
            docs_count=str(docs_count),
            patent=str(patent),
            lastvalue=str(lastvalue),
            utility=str(utility),
            sort_spec=str(sort_spec),
            desc_sort="true" if desc_sort else "false",
        )
        return self.parse_response(response)

    async def async_search(
        self,
        application_number: str,
        docs_start: int = 1,
        docs_count: int = 10,
        patent: bool = True,
        utility: bool = True,
        lastvalue: str = "",
        sort_spec: str = "AD",
        desc_sort: bool = False,
    ) -> pd.DataFrame:
        """
        특허 번호 검색

        Args:
            application_number (str): 특허 번호
            docs_start (int): 검색 시작 위치
            docs_count (int): 검색 결과 수
        """
        logger.info(f"application_number: {application_number}")
        response = await self.async_call(
            api_url=self.api_url,
            application_number=application_number,
            docs_start=str(docs_start),
            docs_count=str(docs_count),
            patent=str(patent),
            lastvalue=str(lastvalue),
            utility=str(utility),
            sort_spec=str(sort_spec),
            desc_sort="true" if desc_sort else "false",
        )
        return self.parse_response(response)
