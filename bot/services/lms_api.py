"""LMS Backend API client."""

import httpx

from config import settings


class LMSAPIError(Exception):
    """Exception raised when LMS API call fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class LMSAPIClient:
    """Client for the LMS Backend API."""

    def __init__(self):
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key
        self.timeout = 30.0

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict | list:
        """Make an authenticated request to the LMS API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., "/items/")
            **kwargs: Additional arguments for httpx

        Returns:
            JSON response as dict or list

        Raises:
            LMSAPIError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.api_key}"
        headers["Content-Type"] = "application/json"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise LMSAPIError(
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. "
                f"The backend service returned an error."
            ) from e
        except httpx.ConnectError as e:
            raise LMSAPIError(
                f"Connection refused ({self.base_url}). "
                f"Check that the backend services are running."
            ) from e
        except httpx.TimeoutException as e:
            raise LMSAPIError(
                f"Request timed out after {self.timeout}s. "
                f"The backend may be overloaded."
            ) from e
        except Exception as e:
            raise LMSAPIError(
                f"Unexpected error connecting to backend: {str(e)}"
            ) from e

    async def get_items(self) -> list[dict]:
        """Fetch all items (labs and tasks) from the backend."""
        return await self._request("GET", "/items/")

    async def get_pass_rates(self, lab_id: str) -> list[dict]:
        """Fetch pass rates for a specific lab.

        Args:
            lab_id: Lab identifier (e.g., "lab-04")

        Returns:
            List of pass rate records
        """
        return await self._request(
            "GET",
            "/analytics/pass-rates",
            params={"lab": lab_id},
        )

    async def health_check(self) -> dict:
        """Check if the backend is healthy and get item count.

        Returns:
            Dict with 'healthy' status and 'item_count'
        """
        items = await self.get_items()
        return {"healthy": True, "item_count": len(items)}


# Global client instance
lms_api = LMSAPIClient()
