import pytest

from mcp_kipris.kipris.tools.korean.applicant_search_tool import PatentApplicantSearchTool


@pytest.mark.asyncio
async def test_run_tool_async_with_valid_input():
    tool = PatentApplicantSearchTool()
    args = {
        "applicant": "삼성전자",
        "docs_start": 1,
        "docs_count": 5,
        "patent": True,
        "utility": True,
        "lastvalue": "",
        "sort_spec": "AD",
        "desc_sort": True,
    }
    results = await tool.run_tool_async(args)
    print(results)
    assert results, "결과가 비어 있으면 안 됩니다."
    assert isinstance(results[0].text, str)
    # assert "삼성전자" in results[0].text or "출원" in results[0].text  # 실제 데이터에 따라 다를 수 있음
