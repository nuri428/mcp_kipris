try:
    from ._version import version as __version__  # type: ignore
except ImportError:
    __version__ = "0.0.0"


def main() -> None:
    import asyncio
    from mcp_kipris.server import main as _async_main

    asyncio.run(_async_main())
