import typing as t
import urllib.parse
from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value

logger = getLogger("mcp-kipris")


class TrademarkSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/kipo-api/kipi/trademarkInfoSearchService/getWordSearch"
        self.KEY_STRING = "response.body.items.item"

    def sync_search(
        self,
        word: str,
        page_no: int = 1,
        num_of_rows: int = 10,
        desc_sort: bool = False,
        sort_spec: str = "AD",
        **kwargs,
    ) -> pd.DataFrame:
        """상표 검색

        Args:
            word (str): 상표 검색 키워드
            page_no (int, optional): 페이지 번호. Defaults to 1.
            num_of_rows (int, optional): 페이지당 행 수. Defaults to 10.
            desc_sort (bool, optional): 내림차순 정렬. Defaults to False.
            sort_spec (str, optional): 정렬 기준. Defaults to "AD".
            **kwargs: 추가 키워드 인자
        Returns:
            pd.DataFrame: 검색 결과
        """
        # url encoding 제거. urlencode를 sync_call, async_call에서 처리함.
        parameters = {**kwargs}

        logger.info(f"word: {word}")
        logger.info(f"parameters: {parameters}")

        response = self.sync_call(
            api_url=self.api_url,
            api_key_field="ServiceKey",
            search_string=word,
            page_no=str(page_no),
            num_of_rows=str(num_of_rows),
            desc_sort="true" if desc_sort else "false",
            sort_spec=str(sort_spec),
            **parameters,
        )
        return self.parse_response(response)

    async def async_search(
        self,
        word: str,
        page_no: int = 1,
        num_of_rows: int = 10,
        desc_sort: bool = False,
        sort_spec: str = "AD",
        **kwargs,
    ) -> pd.DataFrame:
        """상표 검색 (비동기)

        Args:
            word (str): 상표 검색 키워드
            page_no (int, optional): 페이지 번호. Defaults to 1.
            num_of_rows (int, optional): 페이지당 행 수. Defaults to 10.
            desc_sort (bool, optional): 내림차순 정렬. Defaults to False.
            sort_spec (str, optional): 정렬 기준. Defaults to "AD".
            **kwargs: 추가 키워드 인자
        Returns:
            pd.DataFrame: 검색 결과
        """
        # url encoding 제거. urlencode를 sync_call, async_call에서 처리함.
        parameters = {**kwargs}

        logger.info(f"word: {word}")
        logger.info(f"parameters: {parameters}")

        response = await self.async_call(
            api_url=self.api_url,
            api_key_field="ServiceKey",
            search_string=word,
            page_no=str(page_no),
            num_of_rows=str(num_of_rows),
            desc_sort="true" if desc_sort else "false",
            sort_spec=str(sort_spec),
            **parameters,
        )
        return self.parse_response(response)
