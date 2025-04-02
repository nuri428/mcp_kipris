import typing as t
import urllib.parse
from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value

logger = getLogger("mcp-kipris")


class PatentSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch"

    def search(
        self,
        word: str,
        patent: bool = True,
        utility: bool = True,
        lastvalue: str = "",
        page_no: int = 1,
        num_of_rows: int = 10,
        desc_sort: bool = False,
        sort_spec: str = "AD",
        **kwargs,
    ) -> pd.DataFrame:
        """_summary_

        Args:
            word (str): 자유검색 키워드
            patent (bool, optional): 검색 결과에서 특허 포함 여부. Defaults to True.
            utility (bool, optional): 검색 결과에서 실용신안 포함 여부. Defaults to True.
            lastvalue (str, optional): 발명/특허의 상태 코드 검색 Defaults to "".
            page_no (int, optional): 페이지 번호. Defaults to 1.
            num_of_rows (int, optional): 페이지당 행 수. Defaults to 10.
            desc_sort (bool, optional): 내림차순 정렬. Defaults to False.
            sort_spec (str, optional): 정렬 기준. Defaults to "AD".
            **kwargs: 추가 키워드 인자
                invention_title (str, optional): 발명의 제목에서 검색시 키워드.
                abst_cont (str, optional): 발명의 개요에서 검색시 키워드.
                claim_scope (str, optional): 청구범위에서 검색시 키워드.
                ipc_number (str, optional): IPC번호에서 검색 출원번호.
                application_number (str, optional): 출원번호에서 검색 출원번호.
                open_number (str, optional): 공개번호에서 검색 공개번호.
                register_number (str, optional): 등록번호에서 검색 등록번호.
                priority_application_number (str, optional): 우선출원번호에서 검색 우선출원번호.
                international_application_number (str, optional): 국제출원번호에서 검색 국제출원번호.
                international_open_number (str, optional): 국제공개번호에서 검색 국제공개번호.
                application_date (str, optional): 출원일에서 검색 출원일.
                open_date (str, optional): 공개일에서 검색 공개일.
                publication_date (str, optional): 공고일에서 검색 공고일.
                register_date (str, optional): 등록일에서 검색 등록일.
                priority_application_date (str, optional): 우선출원일에서 검색
                international_application_date (str, optional): 국제출원일에서 검색
                international_open_date (str, optional): 국제공개일에서 검색 국제공개일.
                applicant (str, optional): 출원인에서 검색
                inventor (str, optional): 발명자에서 검색
                agent (str, optional): 대리인에서 검색
                right_holder (str, optional): 권리취득인에서 검색
        Returns:
            pd.DataFrame: _description_
        """
        # url encoding 제거. urlencode를 sync_call, async_call에서 처리함.
        parameters = {**kwargs}

        logger.info(f"word: {word}")
        logger.info(f"parameters: {parameters}")

        response = self.sync_call(
            api_url=self.api_url,
            api_key_field="ServiceKey",
            word=word,
            patent="true" if patent else "false",
            utility="true" if utility else "false",
            page_no=str(page_no),
            num_of_rows=str(num_of_rows),
            lastvalue=str(lastvalue),
            desc_sort="true" if desc_sort else "false",
            sort_spec=str(sort_spec),
            **parameters,
        )
        patents = get_nested_key_value(response, "response.body.items.item")
        if patents is None:
            logger.info("patents is None")
            return pd.DataFrame()
        if isinstance(patents, t.Dict):
            patents = [patents]
        return pd.DataFrame(patents)
