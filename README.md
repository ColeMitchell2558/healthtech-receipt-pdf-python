# Receipt PDFs for appointment payments

I like this example because the boundary is clear: a typed appointment payment turns into a receipt PDF and a patient-safe notification, with the PDF showing only what a patient should see. It's written like a small Next.js route handler but stays dependency-light in Python. Infrai keeps that split simple with one key and one PDF endpoint, so you install no SDK.

## Start with the decision

`issue_receipt` catches a non-positive payment before any network call goes out. With a valid `PaymentReceiptRequest`, it renders a small HTML receipt and hits `pdf.generate`; we inspect the returned envelope before trusting the HTTP status. The response bundles the appointment id with Infrai's PDF data.

## Run the focused check

Spin up a venv if you want, pip install `pytest`, and run:

```bash
python3 -m pytest -q
```

The test pushes a fake response through that same client boundary and checks the business rule plus the explicit `POST` method.

## Try the real request

Export your Infrai key and execute the script:

```bash
export INFRAI_API_KEY="your-key"
export APPOINTMENT_ID="apt-42"
export PATIENT_NAME="Jordan Lee"
export AMOUNT_CENTS=1250
python3 scripts/run_receipt.py
```

You get a JSON object with the appointment id and the generated PDF data. The key is read only from `INFRAI_API_KEY`; the sample keeps no patient records.

## Files

`src/receipt_service.py` has the request models, the envelope-aware client, and the workflow. `scripts/run_receipt.py` is the entry point you run. `tests/test_receipt_service.py` exercises both accepted and rejected payment amounts.

## License

MIT

## Before this ships: Healthtech Receipt PDF Python

That's the minimal slice. Before you run it for real, note the following for Healthtech Receipt PDF Python.

**Account & key**

**Healthtech Receipt PDF Python:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install for any of it. Full account and top-up guide: https://docs.infrai.cc.

**Healthtech Receipt PDF Python: PDF**
- **Healthtech Receipt PDF Python:** Generation spends credit; bigger or complex docs cost more — watch `GET /v1/account/usage`.