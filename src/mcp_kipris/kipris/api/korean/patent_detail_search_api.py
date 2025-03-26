from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value
import typing as t
import urllib.parse
from logging import getLogger


logger = getLogger("mcp-kipris")

class PatentDetailSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getBibliographyDetailInfoSearch"

    def search(self, application_number:str, **kwargs)->t.Dict:
        """_summary_

        Args:
            application_number (str): 출원번호
        Returns:
            pd.DataFrame: _description_
        """
        # url encoding
        if application_number :
            application_number = urllib.parse.quote(application_number)
            
        parameters = {**kwargs}
        for key, value in parameters.items():
            parameters[key] = urllib.parse.quote(value)
        
        logger.info(f"application_number: {application_number}")
        
        response = self.common_call(api_url=self.api_url,
                                  api_key_field="ServiceKey",
                                  application_number=application_number)
        patents = get_nested_key_value(response, "response.body.item")
        logger.info(patents)
        if patents is None:
            logger.info("patents is None")
            return {}
        return patents