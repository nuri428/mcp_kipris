import typing as t
import urllib.parse
from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value

logger = getLogger("mcp-kipris")


class PatentDetailSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = (
            "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getBibliographyDetailInfoSearch"
        )

    def sync_search(self, application_number: str, **kwargs) -> pd.DataFrame:
        """_summary_

        Args:
            application_number (str): 출원번호
        Returns:
            pd.DataFrame: _description_
        """
        # url encoding 제거. urlencode를 sync_call, async_call에서 처리함.
        parameters = {**kwargs}
        logger.info(f"application_number: {application_number}")

        response = self.sync_call(
            api_url=self.api_url, api_key_field="ServiceKey", application_number=application_number
        )
        patents = get_nested_key_value(response, "response.body.item")
        logger.info(patents)
        if patents is None:
            logger.info("patents is None")
            return pd.DataFrame()
        if isinstance(patents, t.Dict):
            patents = [patents]
        df = pd.DataFrame(patents)
        return df

    async def async_search(self, application_number: str, **kwargs) -> pd.DataFrame:
        """_summary_

        Args:
            application_number (str): 출원번호
        Returns:
            pd.DataFrame: _description_
        """
        # url encoding 제거. urlencode를 sync_call, async_call에서 처리함.
        parameters = {**kwargs}
        logger.info(f"application_number: {application_number}")

        response = await self.async_call(
            api_url=self.api_url, api_key_field="ServiceKey", application_number=application_number
        )
        patents = get_nested_key_value(response, "response.body.item")
        logger.info(patents)
        if patents is None:
            logger.info("patents is None")
            return pd.DataFrame()
        if isinstance(patents, t.Dict):
            patents = [patents]
        df = pd.DataFrame(patents)
        return df


#         if not df.empty:
#             first = df.iloc[0]
#             summary = f"""
# 📄 **특허 상세 정보**

# - **출원번호**: {first.get("ApplicationNumber", "")}
# - **출원일자**: {first.get("ApplicationDate", "")}
# - **출원인**: {first.get("Applicant", "")}
# - **발명의 명칭**: {first.get("InventionName", "")}
# - **초록**: {first.get("Abstract", "")[:200]}...
# """
#             return pd.DataFrame([{"Summary": summary.strip()}])
# return df
