import typing as t
from logging import getLogger

import pandas as pd
from kipris.tools.abc import ToolHandler
from pydantic import BaseModel, Field, ValidationError, field_validator

from mcp_kipris.kipris.api.foreign import ForeignPatentInternationalApplicationNumberSearchAPI
from mcp_kipris.kipris.api.foreign.code import country, sort_field_dict

logger = getLogger("mcp-kipris")


class ForeignPatentInternationalApplicationNumberSearchArgs(BaseModel):
    international_application_number: str = Field(
        ..., description="International application number, it must be filled"
    )
    current_page: int = Field(1, description="Current page number")
    sort_field: str = Field("AD", description="Sort field")
    sort_state: bool = Field(True, description="Sort state")
    collection_values: str = Field(
        "US",
        description="Collection values, must be one of: US(미국), EP(유럽), WO(PCT), JP(일본), PJ(일본영문초록), CP(중국), CN(중국특허영문초록), TW(대만영문초록), RU(러시아), CO(콜롬비아), SE(스웨덴), ES(스페인), IL(이스라엘)",
    )

    @field_validator("collection_values")
    @classmethod
    def validate_collection_values(cls, v: str) -> str:
        if v not in country:
            raise ValueError(f"collection_values must be one of: {', '.join(country.keys())}")
        return v

    @field_validator("sort_field")
    @classmethod
    def validate_sort_field(cls, v: str) -> str:
        if v not in sort_field_dict:
            raise ValueError(f"sort_field must be one of: {', '.join(sort_field_dict.keys())}")
        return v


class ForeignPatentInternationalApplicationNumberSearchTool(ToolHandler):
    name: str = "foreign_patent_international_application_number_search"
    description: str = "foreign patent search by international application number, this tool is for foreign(US, EP, WO, JP, PJ, CP, CN, TW, RU, CO, SE, ES, IL) patent search"
    api: ForeignPatentInternationalApplicationNumberSearchAPI = ForeignPatentInternationalApplicationNumberSearchAPI()
    args_schema: t.Type[BaseModel] = ForeignPatentInternationalApplicationNumberSearchArgs

    def run_tool(self, args: dict) -> pd.DataFrame:
        try:
            validated_args = ForeignPatentInternationalApplicationNumberSearchArgs(**args)
            logger.info(f"international_application_number: {validated_args.international_application_number}")

            result = self.api.search(
                international_application_number=validated_args.international_application_number,
                current_page=validated_args.current_page,
                sort_field=validated_args.sort_field,
                sort_state=validated_args.sort_state,
                collection_values=validated_args.collection_values,
            )
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            error_details = e.errors()
            for error in error_details:
                field = error["loc"][0]
                if field == "international_application_number":
                    raise ValueError("Invalid input: 국제출원번호(international_application_number) 정보가 필요합니다.")
                elif field == "collection_values":
                    raise ValueError(
                        f"Invalid input: 국가 코드(collection_values)는 다음 중 하나여야 합니다: {', '.join(country.keys())}"
                    )
                elif field == "sort_field":
                    raise ValueError(
                        f"Invalid input: 정렬 기준(sort_field)은 다음 중 하나여야 합니다: {', '.join(sort_field_dict.keys())}"
                    )
            raise ValueError("Invalid input: 입력값이 올바르지 않습니다.")
