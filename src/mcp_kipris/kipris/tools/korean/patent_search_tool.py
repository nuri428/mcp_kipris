import logging
import typing as t

import pandas as pd
from pydantic import BaseModel, Field, ValidationError

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_search_api import PatentSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentSearchArgs(BaseModel):
    word: str = Field("", description="Search query, default is an empty string. this field can be empty")
    invention_title: t.Optional[str] = Field("", description="Invention title")
    abst_cont: t.Optional[str] = Field("", description="Abstract content")
    claim_scope: t.Optional[str] = Field("", description="Claim scope")
    ipc_number: t.Optional[str] = Field("", description="IPC number")
    application_number: t.Optional[str] = Field("", description="Application number")
    open_number: t.Optional[str] = Field("", description="Open number")
    register_number: t.Optional[str] = Field("", description="Register number")
    priority_application_number: t.Optional[str] = Field("", description="Priority application number")
    international_application_number: t.Optional[str] = Field("", description="International application number")
    international_open_number: t.Optional[str] = Field("", description="International open number")
    application_date: t.Optional[str] = Field("", description="Application date")
    open_date: t.Optional[str] = Field("", description="Open date")
    publication_date: t.Optional[str] = Field("", description="Publication date")
    register_date: t.Optional[str] = Field("", description="Register date")
    priority_application_date: t.Optional[str] = Field("", description="Priority application date")
    international_application_date: t.Optional[str] = Field("", description="International application date")
    international_open_date: t.Optional[str] = Field("", description="International open date")
    applicant: t.Optional[str] = Field("", description="Applicant")
    inventor: t.Optional[str] = Field("", description="Inventor")
    agent: t.Optional[str] = Field("", description="Agent")
    right_holder: t.Optional[str] = Field("", description="Right holder")
    patent: bool = Field(True, description="Include patents, default is True")
    utility: bool = Field(True, description="Include utility, default is True")
    lastvalue: t.Optional[str] = Field(
        "",
        description="Patent registration status; (전체:공백입력, 공개:A, 취하:C, 소멸:F, 포기:G, 무효:I, 거절:J, 등록:R)",
    )
    page_no: int = Field(1, description="Start index for documents, default is 0")
    num_of_rows: int = Field(10, description="Number of documents to return, default is 10")
    desc_sort: bool = Field(True, description="Sort in descending order, default is True")
    sort_spec: str = Field(
        "AD",
        description="Field to sort by; default is 'AD'(PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자, FD-국제출원일자, FOD-국제공개일자, RD-우선권주장일자)",
    )


class PatentSearchTool(ToolHandler):
    name: str = "korean_patent_search"
    description: str = "patent search many fields, this tool is for korean patent search"
    api: PatentSearchAPI = PatentSearchAPI()
    args_schema: t.Type[BaseModel] = PatentSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = PatentSearchArgs(**args)
            logger.info(f"search_word: {validated_args.word}")

            result = self.api.search(
                search_word=validated_args.word,
                patent=validated_args.patent,
                utility=validated_args.utility,
                lastvalue=validated_args.lastvalue,
                docs_start=validated_args.docs_start,
                docs_count=validated_args.docs_count,
                sort_spec=validated_args.sort_spec,
                desc_sort=validated_args.desc_sort,
            )
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Invalid input: 검색어(search_word) 정보가 필요합니다.")
