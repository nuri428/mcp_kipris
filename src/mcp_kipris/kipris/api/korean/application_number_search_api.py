from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value
import typing as t
import pandas as pd
from logging import getLogger

logger = getLogger("mcp-kipris")

class PatentApplicationNumberSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.api_url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/applicantNameSearchInfo"
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/applicationNumberSearchInfo"
    def search(self, application_number:str,
        docs_start:int=1,
        docs_count:int=10,
        patent:bool=True,
        utility:bool=True,
        lastvalue:str="",
        sort_spec:str="AD",
        desc_sort:bool=False)->pd.DataFrame:
        logger.info(f"application_number: {application_number}")
        response = self.common_call(api_url=self.api_url, application_number=application_number,
                                    docs_start=str(docs_start),
                                    docs_count=str(docs_count),
                                    patent=str(patent),
                                    lastvalue=str(lastvalue),
                                    utility=str(utility),
                                    sort_spec=str(sort_spec),
                                    desc_sort= 'true' if desc_sort else 'false')
        patents = get_nested_key_value(response, "response.body.items.PatentUtilityInfo")
        if patents is None:
            logger.info("patents is None")
            return pd.DataFrame()
        if isinstance(patents, t.Dict):
            patents = [patents]
        return pd.DataFrame(patents)