"""
Agentic System Client - Production Integration

Connects to real agentic system that queries INDRA.
Replaces MockAgenticSystem for production use.
"""
import httpx
from src.models.gateway import AgenticSystemResponse, QueryRequest
import logging

logger = logging.getLogger(__name__)


class AgenticSystemClient:
    """Client for real agentic system"""

    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize agentic system client.

        Args:
            base_url: Base URL of agentic system (e.g., "http://192.168.254.49:8000")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info(f"Agentic system client initialized: {self.base_url}")

    async def query(self, request: QueryRequest) -> AgenticSystemResponse:
        """
        Query agentic system for causal discovery.

        Args:
            request: QueryRequest with user context and query

        Returns:
            AgenticSystemResponse with causal graph

        Raises:
            httpx.HTTPStatusError: If request fails
            ValueError: If response format invalid
        """
        endpoint = f"{self.base_url}/api/v1/causal_discovery"

        logger.info(f"Querying agentic system: {endpoint}")
        logger.debug(f"Request: user_id={request.user_context.user_id}, query={request.query.get('text')}")

        try:
            response = await self.client.post(
                endpoint,
                json=request.model_dump()
            )
            response.raise_for_status()

            # Parse and validate response
            data = response.json()
            agentic_response = AgenticSystemResponse(**data)

            if agentic_response.status == "success" and agentic_response.causal_graph:
                logger.info(f"✅ Received causal graph: {len(agentic_response.causal_graph.nodes)} nodes, "
                           f"{len(agentic_response.causal_graph.edges)} edges")
            else:
                logger.warning(f"⚠️  Agentic system returned status={agentic_response.status}, "
                             f"error={agentic_response.error}")

            return agentic_response

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Agentic system HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"❌ Agentic system request error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Agentic system error: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class AgenticSystemClientSync:
    """Synchronous version of agentic system client (for non-async contexts)"""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"Agentic system client (sync) initialized: {self.base_url}")

    def query(self, request: QueryRequest) -> AgenticSystemResponse:
        """Synchronous query to agentic system"""
        endpoint = f"{self.base_url}/api/v1/causal_discovery"

        logger.info(f"Querying agentic system: {endpoint}")

        payload = request.model_dump()
        logger.debug(f"Request payload: {payload}")

        try:
            response = self.client.post(
                endpoint,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            agentic_response = AgenticSystemResponse(**data)

            if agentic_response.status == "success" and agentic_response.causal_graph:
                logger.info(f"✅ Received causal graph: {len(agentic_response.causal_graph.nodes)} nodes, "
                           f"{len(agentic_response.causal_graph.edges)} edges")
            else:
                logger.warning(f"⚠️  Agentic system returned status={agentic_response.status}, "
                             f"error={agentic_response.error}")

            return agentic_response

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Agentic system HTTP error: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Agentic system error: {e}")
            raise

    def close(self):
        """Close HTTP client"""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
