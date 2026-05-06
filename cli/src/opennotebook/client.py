"""Open Notebook API 客户端"""

import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()


class OpenNotebookClient:
    """Open Notebook API HTTP 客户端"""

    def __init__(
        self,
        server: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.server = server or os.getenv("OPEN_NOTEBOOK_SERVER", "http://localhost:5055")
        self.password = password or os.getenv("OPEN_NOTEBOOK_PASSWORD", "open-notebook-change-me")
        self.timeout = timeout

        # 确保 server URL 格式正确
        if not self.server.startswith("http"):
            self.server = f"http://{self.server}"

        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """懒加载 HTTP 客户端"""
        if self._client is None:
            headers = {}
            if self.password:
                headers["Authorization"] = f"Bearer {self.password}"
            self._client = httpx.Client(
                base_url=self.server,
                headers=headers,
                timeout=self.timeout,
            )
        return self._client

    def close(self):
        """关闭客户端"""
        if self._client:
            self._client.close()
            self._client = None

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """发起 HTTP 请求"""
        url = f"/api{path}"
        response = self.client.request(
            method=method,
            url=url,
            json=data,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET 请求"""
        return self._request("GET", path, params=params)

    def post(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """POST 请求"""
        return self._request("POST", path, data=data)

    def put(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """PUT 请求"""
        return self._request("PUT", path, data=data)

    def delete(self, path: str) -> Dict[str, Any]:
        """DELETE 请求"""
        return self._request("DELETE", path)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# 全局客户端实例（会被 CLI 命令模块覆盖）
_client: Optional[OpenNotebookClient] = None


def get_client(
    server: Optional[str] = None,
    password: Optional[str] = None,
) -> OpenNotebookClient:
    """获取或创建客户端实例"""
    global _client
    _client = OpenNotebookClient(server=server, password=password)
    return _client