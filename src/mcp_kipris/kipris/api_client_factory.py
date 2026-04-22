"""
Unified API client factory for KIPRIS MCP server.
Provides centralized API client management with consistent configuration.
"""

import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI
from mcp_kipris.kipris.api.korean.patent_search_api import PatentSearchAPI
from mcp_kipris.kipris.api.korean.patent_detail_search_api import PatentDetailSearchAPI
from mcp_kipris.kipris.api.korean.free_search_api import PatentFreeSearchAPI
from mcp_kipris.kipris.api.korean.applicant_search_api import PatentApplicantSearchAPI
from mcp_kipris.kipris.api.korean.patent_summary_search_api import PatentSummarySearchAPI
from mcp_kipris.kipris.api.korean.righter_search_api import PatentRighterSearchAPI
from mcp_kipris.kipris.api.korean.application_number_search_api import PatentApplicationNumberSearchAPI
from mcp_kipris.kipris.api.korean.ipc_search_api import IpcSearchAPI
from mcp_kipris.kipris.api.korean.patent_agent_search_api import PatentAgentSearchAPI
from mcp_kipris.kipris.api.korean.trademark_search_api import TrademarkSearchAPI
from mcp_kipris.kipris.api.foreign.free_search_api import ForeignPatentFreeSearchAPI
from mcp_kipris.kipris.api.foreign.application_number_search import ForeignPatentApplicationNumberSearchAPI
from mcp_kipris.kipris.api.foreign.applicant_search import ForeignPatentApplicantSearchAPI
from mcp_kipris.kipris.api.foreign.international_application_number_search import (
    ForeignPatentInternationalApplicationNumberSearchAPI,
)
from mcp_kipris.kipris.api.foreign.international_open_number_search import ForeignPatentInternationalOpenNumberSearchAPI


@dataclass
class ApiClientConfig:
    """Configuration for API clients."""

    api_key: str
    max_retries: int = 3
    base_delay: float = 1.0
    rate_limit_per_minute: int = 60
    timeout_connect: int = 60
    timeout_read: int = 600


class ApiClientFactory:
    """Factory for creating KIPRIS API clients with consistent configuration."""

    def __init__(self, config: ApiClientConfig):
        self.config = config
        self._clients = {}

    def get_korean_patent_search_client(self) -> PatentSearchAPI:
        """Get Korean patent search API client."""
        key = "korean_patent_search"
        if key not in self._clients:
            self._clients[key] = PatentSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_patent_detail_client(self) -> PatentDetailSearchAPI:
        """Get Korean patent detail API client."""
        key = "korean_patent_detail"
        if key not in self._clients:
            self._clients[key] = PatentDetailSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_free_search_client(self) -> PatentFreeSearchAPI:
        """Get Korean free search API client."""
        key = "korean_free_search"
        if key not in self._clients:
            self._clients[key] = PatentFreeSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_applicant_search_client(self) -> PatentApplicantSearchAPI:
        """Get Korean applicant search API client."""
        key = "korean_applicant_search"
        if key not in self._clients:
            self._clients[key] = PatentApplicantSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_patent_summary_client(self) -> PatentSummarySearchAPI:
        """Get Korean patent summary API client."""
        key = "korean_patent_summary"
        if key not in self._clients:
            self._clients[key] = PatentSummarySearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_righter_search_client(self) -> PatentRighterSearchAPI:
        """Get Korean righter search API client."""
        key = "korean_righter_search"
        if key not in self._clients:
            self._clients[key] = PatentRighterSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_application_number_search_client(self) -> PatentApplicationNumberSearchAPI:
        """Get Korean application number search API client."""
        key = "korean_application_number_search"
        if key not in self._clients:
            self._clients[key] = PatentApplicationNumberSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_ipc_search_client(self) -> IpcSearchAPI:
        """Get Korean IPC search API client."""
        key = "korean_ipc_search"
        if key not in self._clients:
            self._clients[key] = IpcSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_patent_agent_search_client(self) -> PatentAgentSearchAPI:
        """Get Korean patent agent search API client."""
        key = "korean_patent_agent_search"
        if key not in self._clients:
            self._clients[key] = PatentAgentSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_korean_trademark_search_client(self) -> TrademarkSearchAPI:
        """Get Korean trademark search API client."""
        key = "korean_trademark_search"
        if key not in self._clients:
            self._clients[key] = TrademarkSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_foreign_free_search_client(self) -> ForeignPatentFreeSearchAPI:
        """Get foreign free search API client."""
        key = "foreign_free_search"
        if key not in self._clients:
            self._clients[key] = ForeignPatentFreeSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_foreign_application_number_search_client(self) -> ForeignPatentApplicationNumberSearchAPI:
        """Get foreign application number search API client."""
        key = "foreign_application_number_search"
        if key not in self._clients:
            self._clients[key] = ForeignPatentApplicationNumberSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_foreign_applicant_search_client(self) -> ForeignPatentApplicantSearchAPI:
        """Get foreign applicant search API client."""
        key = "foreign_applicant_search"
        if key not in self._clients:
            self._clients[key] = ForeignPatentApplicantSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_foreign_international_application_number_search_client(
        self,
    ) -> ForeignPatentInternationalApplicationNumberSearchAPI:
        """Get foreign international application number search API client."""
        key = "foreign_international_application_number_search"
        if key not in self._clients:
            self._clients[key] = ForeignPatentInternationalApplicationNumberSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_foreign_international_open_number_search_client(self) -> ForeignPatentInternationalOpenNumberSearchAPI:
        """Get foreign international open number search API client."""
        key = "foreign_international_open_number_search"
        if key not in self._clients:
            self._clients[key] = ForeignPatentInternationalOpenNumberSearchAPI(api_key=self.config.api_key)
        return self._clients[key]

    def get_all_korean_clients(self) -> t.Dict[str, ABSKiprisAPI]:
        """Get all Korean API clients."""
        return {
            "patent_search": self.get_korean_patent_search_client(),
            "patent_detail": self.get_korean_patent_detail_client(),
            "free_search": self.get_korean_free_search_client(),
            "applicant_search": self.get_korean_applicant_search_client(),
            "patent_summary": self.get_korean_patent_summary_client(),
            "righter_search": self.get_korean_righter_search_client(),
            "application_number_search": self.get_korean_application_number_search_client(),
            "ipc_search": self.get_korean_ipc_search_client(),
            "patent_agent_search": self.get_korean_patent_agent_search_client(),
            "trademark_search": self.get_korean_trademark_search_client(),
        }

    def get_all_foreign_clients(self) -> t.Dict[str, ABSKiprisAPI]:
        """Get all foreign API clients."""
        return {
            "free_search": self.get_foreign_free_search_client(),
            "application_number_search": self.get_foreign_application_number_search_client(),
            "applicant_search": self.get_foreign_applicant_search_client(),
            "international_application_number_search": self.get_foreign_international_application_number_search_client(),
            "international_open_number_search": self.get_foreign_international_open_number_search_client(),
        }

    def get_all_clients(self) -> t.Dict[str, ABSKiprisAPI]:
        """Get all API clients."""
        all_clients = {}
        all_clients.update(self.get_all_korean_clients())
        all_clients.update(self.get_all_foreign_clients())
        return all_clients


# Global factory instance
_factory: t.Optional[ApiClientFactory] = None


def get_api_client_factory(api_key: str) -> ApiClientFactory:
    """
    Get or create the global API client factory.

    Args:
        api_key: KIPRIS API key

    Returns:
        ApiClientFactory instance
    """
    global _factory

    if _factory is None:
        config = ApiClientConfig(api_key=api_key)
        _factory = ApiClientFactory(config)

    return _factory


def reset_factory() -> None:
    """Reset the global factory (useful for testing)."""
    global _factory
    _factory = None
