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

    @staticmethod
    def _format_validation_detail(detail: list) -> str:
        field_names = {
            "idacidente": "ID do acidente",
            "idlocal": "ID do local",
            "idveiculo": "ID do veículo",
            "estado": "Estado",
            "cidade": "Cidade",
            "bairro": "Bairro",
            "rua": "Rua",
            "data_acidente": "Data do acidente",
            "hora_acidente": "Hora do acidente",
            "qtd_vitimas": "Quantidade de vítimas",
            "qtd_veiculos": "Quantidade de veículos",
            "tipos_veiculos": "Tipos de veículos",
            "nome_clima": "Clima",
            "tipo_gravidade": "Gravidade",
            "nome_veiculo": "Tipo de veículo",
        }
        error_messages = {
            "int_parsing": "deve ser um número inteiro",
            "int_type": "deve ser um número inteiro",
            "date_from_datetime_parsing": "deve ser uma data válida (AAAA-MM-DD)",
            "date_parsing": "deve ser uma data válida (AAAA-MM-DD)",
            "time_parsing": "deve ser um horário válido (HH:MM)",
            "string_type": "deve ser um texto",
            "list_type": "deve ser uma lista",
            "missing": "é obrigatório",
            "string_too_long": "excede o tamanho máximo permitido",
            "too_long": "excede o tamanho máximo permitido",
            "int_from_float": "deve ser um número inteiro",
            "string_pattern_mismatch": "está em um formato inválido",
            "enum": "selecione uma opção válida",
        }

        messages = []
        for error in detail:
            if not isinstance(error, dict):
                continue

            location = error.get("loc", [])
            fields = [
                str(part)
                for part in location
                if part not in {"body", "query", "path"}
            ]
            field = ".".join(
                field_names.get(part, part) for part in fields
            ) or "Dados"
            error_type = error.get("type")
            context = error.get("ctx") or {}
            message = error_messages.get(error_type)
            if message is None and error_type == "greater_than":
                limit = context.get("gt")
                message = f"deve ser maior que {limit}"
            elif message is None and error_type == "greater_than_equal":
                limit = context.get("ge")
                message = f"deve ser maior ou igual a {limit}"
            elif message is None and error_type == "string_too_short":
                minimum = context.get("min_length")
                message = f"deve conter pelo menos {minimum} caracteres"
            elif message is None and error_type == "too_short":
                minimum = context.get("min_length")
                message = f"deve conter pelo menos {minimum} item(ns)"

            if message is None:
                original_message = error.get("msg")
                if isinstance(original_message, str) and error_type == "value_error":
                    message = original_message.removeprefix("Value error, ")
                else:
                    message = "valor inválido"
            messages.append(f"{field}: {message.rstrip('. ')}.")

        return " ".join(messages) or "Dados inválidos. Verifique os campos informados."

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
            if isinstance(detail, str):
                message = detail
            elif isinstance(detail, list):
                message = self._format_validation_detail(detail)
            else:
                message = error.reason
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