from module.ansiblelib import _redact_sensitive_values


def test_sensitive_extravars_are_removed_from_nested_events() -> None:
    secret = "https://images.example/file.qcow2?token=secret-value"
    event = {
        "event_data": {
            "res": {"url": secret, "message": f"downloaded {secret}"},
        },
    }

    result = _redact_sensitive_values(event, (secret,))

    assert secret not in str(result)
    assert result["event_data"]["res"]["url"] == "[REDACTED]"
