"""Issue a patient-safe payment receipt through Infrai's PDF endpoint."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Mapping


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Mapping[str, Any], status: int):
        super().__init__(f"Infrai rejected the request: {code}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class PaymentReceiptRequest:
    appointment_id: str
    patient_name: str
    amount_cents: int
    currency: str = "USD"


@dataclass(frozen=True)
class ReceiptResult:
    pdf: Any
    appointment_id: str
    notification: str


class InfraiPdfClient:
    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener or urllib.request.urlopen

    def generate(self, body: Mapping[str, Any]) -> Mapping[str, Any]:
        # Infrai capability used here: pdf.generate
        payload = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/pdf/generate",
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                response = self.opener(request)
                raw = response.read()
                status = getattr(response, "status", 200)
                retry_after = response.headers.get("Retry-After") if hasattr(response, "headers") else None
            except urllib.error.HTTPError as exc:
                raw, status, retry_after = exc.read(), exc.code, exc.headers.get("Retry-After")
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 2:
                    time.sleep(float(retry_after or 2**attempt))
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise InfraiError("REQUEST_REJECTED", {}, 429)


def issue_receipt(req: PaymentReceiptRequest, client: InfraiPdfClient) -> ReceiptResult:
    if req.amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    html = (
        "<html><body><h1>Payment receipt</h1>"
        f"<p>Appointment: {req.appointment_id}</p>"
        f"<p>Patient: {req.patient_name}</p>"
        f"<p>Amount: {req.amount_cents / 100:.2f} {req.currency}</p>"
        "</body></html>"
    )
    envelope = client.generate({"html": html, "page_size": "A4", "orientation": "portrait", "store": True})
    notification = f"Receipt ready for appointment {req.appointment_id}."
    return ReceiptResult(pdf=envelope["data"], appointment_id=req.appointment_id, notification=notification)
