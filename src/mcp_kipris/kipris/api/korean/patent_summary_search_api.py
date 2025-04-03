import typing as t
import urllib.parse
from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value

logger = getLogger("mcp-kipris")


class PatentSummarySearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getBibliographySumryInfoSearch"
        self.KEY_STRING = "response.body.items.item"

    def sync_search(self, application_number: str) -> pd.DataFrame:
        """_summary_

        Args:
            application_number (str): 출원번호
        Returns:
            pd.DataFrame: _description_
        """
        if not application_number:
            raise ValueError("application_number is required")

        logger.info(f"application_number: {application_number}")

        response = self.sync_call(
            api_url=self.api_url, api_key_field="ServiceKey", application_number=application_number
        )
        return self.parse_response(response)

    async def async_search(self, application_number: str) -> pd.DataFrame:
        """_summary_

        Args:
            application_number (str): 출원번호
        Returns:
            pd.DataFrame: _description_
        """
        if not application_number:
            raise ValueError("application_number is required")

        logger.info(f"application_number: {application_number}")

        response = await self.async_call(
            api_url=self.api_url, api_key_field="ServiceKey", application_number=application_number
        )
        return self.parse_response(response)
