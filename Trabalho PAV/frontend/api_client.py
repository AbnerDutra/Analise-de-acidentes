import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class APIError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: dict | None = None,
        params: dict[str, str] | None = None,
    ):
        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            url = f"{url}?{urlencode(params)}"

        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=body,
            method=method,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

        try:
            with urlopen(request, timeout=10) as response:
                response_body = response.read()
        except HTTPError as error:
            response_body = error.read()
            try:
                detail = json.loads(response_body.decode("utf-8")).get("detail")
            except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
                detail = None
            message = detail if isinstance(detail, str) else error.reason
            raise APIError(str(message), error.code) from error
        except URLError as error:
            raise APIError(
                f"Não foi possível conectar à API em {self.base_url}: {error.reason}"
            ) from error
        except TimeoutError as error:
            raise APIError(f"A API não respondeu dentro do prazo: {self.base_url}") from error

        if not response_body:
            return None
        try:
            return json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise APIError("A API retornou uma resposta JSON inválida.") from error

    def get(self, path: str, *, params: dict[str, str] | None = None):
        return self.request("GET", path, params=params)

    def post(self, path: str, payload: dict):
        return self.request("POST", path, payload=payload)

    def put(self, path: str, payload: dict):
        return self.request("PUT", path, payload=payload)

    def delete(self, path: str):
        return self.request("DELETE", path)

    @staticmethod
    def resource_path(resource: str, record_id: int) -> str:
        return f"{resource}/{quote(str(record_id), safe='')}"