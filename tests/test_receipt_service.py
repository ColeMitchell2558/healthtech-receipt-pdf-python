import json

import pytest

from src.receipt_service import InfraiPdfClient, PaymentReceiptRequest, issue_receipt


class FakeResponse:
    status = 200
    headers = {}

    def read(self):
        return json.dumps({"ok": True, "data": {"pdf": "receipt-123"}, "error": None, "metadata": {}}).encode()


def test_positive_payment_produces_receipt():
    captured = {}

    def opener(request):
        captured["method"] = request.method
        captured["body"] = json.loads(request.data)
        return FakeResponse()

    result = issue_receipt(PaymentReceiptRequest("apt-42", "Jordan Lee", 1250), InfraiPdfClient("test-key", opener))
    assert result.appointment_id == "apt-42"
    assert result.pdf["pdf"] == "receipt-123"
    assert result.notification == "Receipt ready for appointment apt-42."
    assert captured["method"] == "POST"
    assert "patient_name" not in captured["body"]


def test_zero_amount_is_rejected_before_api_call():
    with pytest.raises(ValueError, match="positive"):
        issue_receipt(PaymentReceiptRequest("apt-42", "Jordan Lee", 0), InfraiPdfClient("test-key", lambda _: None))
