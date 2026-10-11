import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.receipt_service import InfraiPdfClient, PaymentReceiptRequest, issue_receipt


def main() -> None:
    receipt = issue_receipt(
        PaymentReceiptRequest(
            appointment_id=os.environ.get("APPOINTMENT_ID", "apt-demo-1"),
            patient_name=os.environ.get("PATIENT_NAME", "Demo Patient"),
            amount_cents=int(os.environ.get("AMOUNT_CENTS", "1250")),
        ),
        InfraiPdfClient(),
    )
    print(json.dumps({"appointment_id": receipt.appointment_id, "pdf": receipt.pdf, "notification": receipt.notification}, indent=2))


if __name__ == "__main__":
    main()
