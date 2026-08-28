"""Agent API内で使用する、外部へ安全に変換可能な例外。"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mixin.exception import ApiErrorCode


class AgentError(Exception):
    """利用者へ公開できるcodeを持つAgent API例外。"""

    # workerでは入力・policy競合を「外部効果なし」としてfailedへ確定できる。
    # adapterの予期しない例外はこの型ではないためunknownのまま扱われる。
    outcome_unknown = False
    retryable = False
    safe_message = True

    def __init__(
        self,
        code: ApiErrorCode | str,
        detail: str,
        status_code: int = 400,
    ) -> None:
        # catalogは依存を限定したMCP contract testからもimportされるため、
        # FastAPIを必要とする共通serializerは例外生成時まで読み込まない。
        from mixin.exception import ApiErrorCode, agent_error_message

        super().__init__(detail)
        self.code = ApiErrorCode(code)
        self.error_code = self.code
        self.detail = detail
        self.status_code = status_code
        self.api_message = agent_error_message(status_code)


class AuthenticationError(AgentError):
    def __init__(self, code: ApiErrorCode | str, detail: str) -> None:
        super().__init__(code, detail, 401)


class AuthorizationError(AgentError):
    def __init__(self, code: ApiErrorCode | str, detail: str) -> None:
        super().__init__(code, detail, 403)


class ConflictError(AgentError):
    def __init__(self, code: ApiErrorCode | str, detail: str) -> None:
        super().__init__(code, detail, 409)


class NotFoundError(AgentError):
    def __init__(self, code: ApiErrorCode | str, detail: str) -> None:
        super().__init__(code, detail, 404)


class ServiceUnavailableError(AgentError):
    def __init__(self, code: ApiErrorCode | str, detail: str) -> None:
        super().__init__(code, detail, 503)


class AuditWriteError(ServiceUnavailableError):
    def __init__(self) -> None:
        super().__init__(
            "audit_unavailable",
            "監査記録を保存できないため操作を拒否しました",
        )
