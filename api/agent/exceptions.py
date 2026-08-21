"""Agent API内で使用する、外部へ安全に変換可能な例外。"""


class AgentError(Exception):
    """利用者へ公開できるcodeを持つAgent API例外。"""

    # workerでは入力・policy競合を「外部効果なし」としてfailedへ確定できる。
    # adapterの予期しない例外はこの型ではないためunknownのまま扱われる。
    outcome_unknown = False
    retryable = False
    safe_message = True

    def __init__(self, code: str, detail: str, status_code: int = 400) -> None:
        super().__init__(detail)
        self.code = code
        self.error_code = code
        self.detail = detail
        self.status_code = status_code


class AuthenticationError(AgentError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(code, detail, 401)


class AuthorizationError(AgentError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(code, detail, 403)


class ConflictError(AgentError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(code, detail, 409)


class NotFoundError(AgentError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(code, detail, 404)


class ServiceUnavailableError(AgentError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(code, detail, 503)


class AuditWriteError(ServiceUnavailableError):
    def __init__(self) -> None:
        super().__init__(
            "audit_unavailable",
            "監査記録を保存できないため操作を拒否しました",
        )
