import typing as t
import urllib.parse
from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value

logger = getLogger("mcp-kipris")


class PatentApplicantSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/applicantNameSearchInfo"

    async def async_search(
        self,
        applicant: str,
        docs_start: int = 1,
        docs_count: int = 10,
        patent: bool = True,
        utility: bool = True,
        lastvalue: str = "",
        sort_spec: str = "AD",
        desc_sort: bool = False,
    ) -> pd.DataFrame:
        logger.info(f"applicant: {applicant}")

        response = await self.async_call(
            api_url=self.api_url,
            applicant=applicant,
            docs_start=str(docs_start),
            docs_count=str(docs_count),
            patent=str(patent),
            lastvalue=str(lastvalue),
            utility=str(utility),
            sort_spec=str(sort_spec),
            desc_sort="true" if desc_sort else "false",
        )
        patents = get_nested_key_value(response, "response.body.items.PatentUtilityInfo")
        if patents is None:
            logger.info("patents is None")
            message = get_nested_key_value(response, "response.header.msg")
            if message:
                logger.warning(f"KIPRIS API 응답 메시지: {message}")
            return pd.DataFrame()
        if isinstance(patents, t.Dict):
            patents = [patents]
        df = pd.DataFrame(patents)
        expected_columns = ["Applicant", "InventionName", "ApplicationNumber", "ApplicationDate", "RegistrationStatus"]
        df = df[[col for col in expected_columns if col in df.columns]]
        return df

    def sync_search(
        self,
        applicant: str,
        docs_start: int = 1,
        docs_count: int = 10,
        patent: bool = True,
        utility: bool = True,
        lastvalue: str = "",
        sort_spec: str = "AD",
        desc_sort: bool = False,
    ) -> pd.DataFrame:
        logger.info(f"applicant: {applicant}")

        response = self.sync_call(
            api_url=self.api_url,
            applicant=applicant,
            docs_start=str(docs_start),
            docs_count=str(docs_count),
            patent=str(patent),
            lastvalue=str(lastvalue),
            utility=str(utility),
            sort_spec=str(sort_spec),
            desc_sort="true" if desc_sort else "false",
        )
        patents = get_nested_key_value(response, "response.body.items.PatentUtilityInfo")
        if patents is None:
            logger.info("patents is None")
            message = get_nested_key_value(response, "response.header.msg")
            if message:
                logger.warning(f"KIPRIS API 응답 메시지: {message}")
            return pd.DataFrame()
        if isinstance(patents, t.Dict):
            patents = [patents]
        df = pd.DataFrame(patents)
        expected_columns = ["InventionName", "ApplicationNumber", "ApplicationDate", "Applicant", "RegistrationStatus"]
        df = df[[col for col in expected_columns if col in df.columns]]
        return df
