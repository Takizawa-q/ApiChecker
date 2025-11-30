from curl_cffi.requests import AsyncSession
from typing import Optional, Dict, Any, Union
import asyncio


class RequestSession:
    
    def __init__(
        self,
        impersonate: str = "chrome",
        timeout: int = 30,
        proxy: Optional[str] = None,
        verify: bool = True
    ):
        """
        Initialize the async curl client.
        Args:
            impersonate: Browser to impersonate (e.g., 'chrome', 'firefox', 'safari')
            timeout: Request timeout in seconds
            proxy: Proxy URL (e.g., 'http://proxy:8080')
            verify: Whether to verify SSL certificates
        """
        self.impersonate = impersonate
        self.timeout = timeout
        self.proxy = proxy
        self.verify = verify
        self._session: Optional[AsyncSession] = None
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
    
    async def start(self):
        """Initialize the session."""
        if self._session is None:
            self._session = AsyncSession(impersonate=self.impersonate)
    
    async def close(self):
        """Close the session and cleanup resources."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Any:
        """
        Perform an async GET request.
        
        Args:
            url: Target URL
            params: Query parameters
            headers: Custom headers
            **kwargs: Additional arguments for the request
        
        Returns:
            Response object
        """
        if self._session is None:
            await self.start()
        
        return await self._session.get(
            url,
            params=params,
            headers=headers,
            timeout=kwargs.get('timeout', self.timeout),
            proxy=kwargs.get('proxy', self.proxy),
            verify=kwargs.get('verify', self.verify),
            **{k: v for k, v in kwargs.items() if k not in ['timeout', 'proxy', 'verify']}
        )
    
    async def post(
        self,
        url: str,
        data: Optional[Union[Dict, str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Any:
        """
        Perform an async POST request.
        
        Args:
            url: Target URL
            data: Form data or raw body
            json: JSON data (automatically serialized)
            headers: Custom headers
            **kwargs: Additional arguments for the request
        
        Returns:
            Response object
        """
        if self._session is None:
            await self.start()
        
        return await self._session.post(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=kwargs.get('timeout', self.timeout),
            proxy=kwargs.get('proxy', self.proxy),
            verify=kwargs.get('verify', self.verify),
            **{k: v for k, v in kwargs.items() if k not in ['timeout', 'proxy', 'verify']}
        )
    
    async def put(
        self,
        url: str,
        data: Optional[Union[Dict, str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Any:
        """Perform an async PUT request."""
        if self._session is None:
            await self.start()
        
        return await self._session.put(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=kwargs.get('timeout', self.timeout),
            proxy=kwargs.get('proxy', self.proxy),
            verify=kwargs.get('verify', self.verify),
            **{k: v for k, v in kwargs.items() if k not in ['timeout', 'proxy', 'verify']}
        )
    
    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Any:
        """Perform an async DELETE request."""
        if self._session is None:
            await self.start()
        
        return await self._session.delete(
            url,
            headers=headers,
            timeout=kwargs.get('timeout', self.timeout),
            proxy=kwargs.get('proxy', self.proxy),
            verify=kwargs.get('verify', self.verify),
            **{k: v for k, v in kwargs.items() if k not in ['timeout', 'proxy', 'verify']}
        )
    
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Any:
        """
        Perform a generic async HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Target URL
            **kwargs: Additional arguments for the request
        
        Returns:
            Response object
        """
        if self._session is None:
            await self.start()
        
        return await self._session.request(
            method,
            url,
            timeout=kwargs.get('timeout', self.timeout),
            proxy=kwargs.get('proxy', self.proxy),
            verify=kwargs.get('verify', self.verify),
            **{k: v for k, v in kwargs.items() if k not in ['timeout', 'proxy', 'verify']}
        )
