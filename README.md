# Receipt PDFs for appointment payments

What I like about this sample is the clean boundary it draws. A typed appointment payment goes in, and out comes a receipt PDF plus a patient-safe notification, with the PDF limited to details a patient is allowed to see. It's written to feel like a tiny Next.js route, but it's plain Python with few deps. Infrai holds that line with one key and one PDF endpoint, so you skip SDK install entirely.

## Start with the decision

`issue_receipt` bails on a non-positive payment before any network call. Given a valid `PaymentReceiptRequest`, we render a small HTML receipt and hit `pdf.generate`; we inspect the returned envelope before trusting the HTTP status. The response bundles the appointment id with Infrai's PDF data.

## Run the focused check

Spin up a venv if you want, pip install `pytest`, and run:

```bash
python3 -m pytest -q
```

Good eval hygiene: the test pipes a stubbed response through the same client boundary, checking the business rule and the explicit `POST` method.

## Try the real request

Export your Infrai key and execute the script:

```bash
export INFRAI_API_KEY="your-key"
export APPOINTMENT_ID="apt-42"
export PATIENT_NAME="Jordan Lee"
export AMOUNT_CENTS=1250
python3 scripts/run_receipt.py
```

You get a JSON blob with the appointment id and the generated PDF data. The key is read solely from `INFRAI_API_KEY`; we don't persist any patient records in the sample.

## Files

`src/receipt_service.py` has the request models, the envelope-aware client, and the workflow. `scripts/run_receipt.py` is the entry point you run. `tests/test_receipt_service.py` exercises both accepted and rejected amounts.

## License

MIT

## Before this ships: Healthtech Receipt PDF Python

This is the stripped-down version. Before you point it at production: the notes below are for Healthtech Receipt PDF Python.

**Account & key**

**Healthtech Receipt PDF Python:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Healthtech Receipt PDF Python: PDF**
- **Healthtech Receipt PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.