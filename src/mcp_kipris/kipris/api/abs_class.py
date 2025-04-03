import logging
import os
import typing as t
from urllib.parse import urlencode

import pandas as pd
from dotenv import load_dotenv
from stringcase import camelcase

from mcp_kipris.kipris.api.utils import get_nested_key_value, get_response, get_response_async

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,  # INFO 레벨을 출력
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mcp-kipris")
load_dotenv()


# ic.disable()
class ABSKiprisAPI:
    def __init__(self, **kwargs):
        self.HEADER_KEY_STRING = "response.body.items.item"
        self.KEY_STRING = ""
        if "api_key" in kwargs:
            self.api_key = kwargs["api_key"]
        else:
            if os.getenv("KIPRIS_API_KEY"):
                self.api_key = os.getenv("KIPRIS_API_KEY")
            else:
                raise ValueError(
                    "KIPRIS_API_KEY is not set you must set KIPRIS_API_KEY in .env file or pass api_key to constructor "
                )

    def sync_call(self, api_url: str, api_key_field="accessKey", **params) -> t.Dict:
        """
        KIPRIS API 공통 호출 서비스

        Args:
            api_url (str): 서브 URL
            api_key_field (str): 키 필드 이름
            params (dict): 파라미터

        Returns:
            t.List[dict]: 응답 데이터
        """

        try:
            params_dict = {camelcase(k): v for k, v in params.items() if v is not None and v != ""}
            params_dict[api_key_field] = self.api_key
            full_url = f"{api_url}?{urlencode(params_dict)}"
            logger.info(f"KIPRIS 요청 URL: {full_url}")
            return get_response(full_url)
        except Exception as e:
            logger.error(f"KIPRIS 요청 실패: {e}")
            raise

    async def async_call(self, api_url: str, api_key_field="accessKey", **params) -> t.Dict:
        """
        KIPRIS API 비동기 호출 서비스

        Args:
            api_url (str): 서브 URL
            api_key_field (str): 키 필드 이름
            params (dict): 파라미터

        Returns:
            dict: 응답 데이터
        """
        try:
            params_dict = {camelcase(k): v for k, v in params.items() if v is not None and v != ""}
            params_dict[api_key_field] = self.api_key
            full_url = f"{api_url}?{urlencode(params_dict)}"
            print(full_url)
            logger.info(f"[async] KIPRIS 요청 URL: {full_url}")
            return await get_response_async(full_url)
        except Exception as e:
            logger.error(f"[async] KIPRIS 요청 실패: {e}")
            raise

    def parse_response(self, response: dict) -> pd.DataFrame:
        patents = get_nested_key_value(response, self.KEY_STRING)
        if patents is None:
            logger.info("patents is None")
            message = get_nested_key_value(response, self.HEADER_KEY_STRING)
            if message:
                logger.warning(f"KIPRIS API 응답 메시지: {message}")
            return pd.DataFrame()
        if isinstance(patents, t.Dict):
            patents = [patents]
        return pd.DataFrame(patents)
