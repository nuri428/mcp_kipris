import logging
import typing as t
import urllib.parse

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.utils import get_nested_key_value

logger = logging.getLogger("mcp-kipris")


class PatentFreeSearchAPI(ABSKiprisAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/freeSearchInfo"

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
        # api url https://plus.kipris.or.kr/portal/data/service/DBII_000000000000001/view.do?menuNo=200100&kppBCode=&kppMCode=&kppSCode=&subTab=SC001&entYn=N&clasKeyword=#soap_ADI_0000000000002944

        logger.info(f"word: {word}")
        response = self.sync_call(
            api_url=self.api_url,
            api_key_field="accessKey",
            word=word,
            patent="true" if patent else "false",
            utility="true" if utility else "false",
            page_no=str(page_no),
            num_of_rows=str(num_of_rows),
            lastvalue=str(lastvalue),
            desc_sort="true" if desc_sort else "false",
            sort_spec=str(sort_spec),
            **kwargs,
        )
        patents = get_nested_key_value(response, "response.body.items.PatentUtilityInfo")

        logger.info(patents)
        if patents is None:
            logger.info("patents is None")
            return pd.DataFrame()
        if isinstance(patents, t.Dict):
            patents = [patents]
        patents = pd.DataFrame(patents)
        if "application_number" in patents.columns:
            patents = patents.drop_duplicates(subset=["application_number"])
        if "ApplicationNumber" in patents.columns:
            patents = patents.drop_duplicates(subset=["ApplicationNumber"])
        # <Applicant>주식회사 엘지에너지솔루션</Applicant>
        # <ApplicationDate>20250123</ApplicationDate>
        # <ApplicationNumber>1020250010491</ApplicationNumber>
        # <Abstract>본 출원은 음극 조성물, 리튬 이차 전지용 음극 및 음극을 포함하는 리튬 이차 전지에 관한 것이다.</Abstract>
        # <DrawingPath>http://plus.kipris.or.kr/kiprisplusws/fileToss.jsp?arg=6c650beb4cee9ce4122b704b88878c93369ec08af6388ff6f849fb8e24b833f76963670192e45f9a2d32d89c77a87fce4a9dda16fd43f2e9382520b3c4968d7ce804f2da60a06ff4</DrawingPath>
        # <ThumbnailPath>http://plus.kipris.or.kr/kiprisplusws/fileToss.jsp?arg=ed43a0609e94d6e22d01c5c32ba711cf14196bb3950514c0e5415023c0bad8ab1ad3578b336e1011c4fb1d1ef9fd058878070189afc2f9adc373fee834960addd3564b9fd05899c8</ThumbnailPath>
        # <SerialNumber>1</SerialNumber>
        # <InventionName>음극 조성물, 이를 포함하는 리튬 이차 전지용 음극 및 음극을 포함하는 리튬 이차 전지</InventionName>
        # <InternationalpatentclassificationNumber>H01M 4/62|H01M 4/38|H01M 4/134|H01M 10/0525|H01M 4/02</InternationalpatentclassificationNumber>
        # <OpeningDate>20250204</OpeningDate>
        # <OpeningNumber>1020250017736</OpeningNumber>
        # <PublicNumber/>
        # <PublicDate/>
        # <RegistrationDate/>
        # <RegistrationNumber/>
        # <RegistrationStatus>공개</RegistrationStatus>
        # ["Applicant","ApplicationDate","ApplicationNumber","Abstract","DrawingPath","ThumbnailPath","SerialNumber","InventionName","InternationalpatentclassificationNumber","OpeningDate","OpeningNumber","PublicNumber","PublicDate","RegistrationDate","RegistrationNumber","RegistrationStatus"]
        patents = patents[
            [
                "Applicant",
                "ApplicationDate",
                "ApplicationNumber",
                "Abstract",
                "InventionName",
                "InternationalpatentclassificationNumber",
                "RegistrationStatus",
            ]
        ]
        patents = patents.rename(
            columns={
                "InventionName": "발명의 제목",
                "ApplicationNumber": "출원번호",
                "Abstract": "발명의 개요",
                "InternationalpatentclassificationNumber": "IPC번호",
                "ApplicationDate": "출원일",
                "RegistrationStatus": "등록상태",
                "Applicant": "출원인",
            }
        )
        return patents
