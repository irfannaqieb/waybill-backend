from app.guardrails.pii import redact_pii


def test_redact_email():
    assert "[REDACTED_EMAIL]" in redact_pii("email me at a@b.com")


def test_redact_phone():
    out = redact_pii("call me at +60 12-345-6789 please")
    assert "[REDACTED_PHONE]" in out
