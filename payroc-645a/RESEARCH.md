# Payroc Cloud – technical research for NailFlowApp (PHP, server-side, UAT)

Researched 2026-11-04 from public docs only (docs.payroc.com + search results). No sign-up/login done.
Note: direct curl to docs.payroc.com was blocked by this environment's proxy; pages were read via a
web-fetch summarizer, so long schemas are paraphrased (field names are as reported). Re-check exact
spelling against the live API reference before coding.

Legend: **UNCONFIRMED** = not stated in docs I could read, or docs conflict.

---

## 1. Authentication (API key -> Bearer token)

| Item | Value |
|---|---|
| Method | `POST` |
| Production identity URL | `https://identity.payroc.com/authorize` |
| UAT identity URL | `https://identity.uat.payroc.com/authorize` (shown on the "Pay by Cloud" test page and older guides) |
| Request header | `x-api-key: <your API key>` |
| Request body | none shown (example sends only the header) |
| Response fields | `access_token`, `expires_in` (3600), `scope`, `token_type` (`Bearer`) |
| Lifetime | 1 hour ("Each Bearer token expires after one hour"); generate a new one before expiry |
| Use on API calls | `Authorization: Bearer <access_token>` |

**CONFLICT / UNCONFIRMED:** the current Authentication page and the current "Payroc Cloud" test page say:
"We automatically send requests that use a test API key to our test environment, so you don't need to change the
endpoint" (i.e. always `identity.payroc.com` + `api.payroc.com`). Older and other pages (Pay by Cloud test page,
refund guides, Hosted Fields) still list `identity.uat.payroc.com` / `api.uat.payroc.com`.
Recommendation: make both hosts config values (`PAYROC_IDENTITY_URL`, `PAYROC_API_BASE`); try the UAT hosts first
with the UAT key and fall back to production hosts if the Payroc integration engineer says so.

Two key types (Knowledge > API keys):
- **API key** – given by Payroc at signup; used with the identity service to get Bearer tokens (this is what the PHP server uses).
- **Payroc App API key** – created in the Self-Care Portal (`https://payments.payroc.com/merchant/selfcare` > Settings > API Keys > NEW API KEY; permissions Account/Customer/Transaction/Bank Transfer/Reporting; pick processing terminals). Used by the Payroc App on the device and by the **Payroc Cloud Simulator**, not by the server.

Sources:
- https://docs.payroc.com/api/authentication
- https://docs.payroc.com/test/test-your-integration/payroc-cloud
- https://docs.payroc.com/test/test-your-integration/pay-by-cloud
- https://docs.payroc.com/knowledge/basic-concepts/api-keys
- https://docs.payroc.com/test/test-your-integration/payroc-cloud-simulator/generate-a-payroc-app-api-key

## 2. Base URLs

| Env | API base | Identity |
|---|---|---|
| Production | `https://api.payroc.com/v1` | `https://identity.payroc.com/authorize` |
| UAT / test | `https://api.uat.payroc.com/v1` | `https://identity.uat.payroc.com/authorize` |
| Cloud Simulator (web app, browser) | `https://cloud.uat.payroc.com` | – |

- See conflict note in section 1 (test keys may auto-route through production hosts).
- Postman collection uses an environment named **"Payroc-UAT"** (no URLs printed on the page).
- Official PHP SDK exists: Packagist `payroc/payroc-sdk-php` (README says `composer require payroc/payroc` – name inconsistent, **UNCONFIRMED** which is right), PHP ^8.1, source `https://github.com/payroc/payroc-sdk-php`, `Environments::Production()` and `Environments::custom(api:, identity:)`. Whether it has a built-in UAT environment and Payroc Cloud methods: **UNCONFIRMED**. Status: "Beta".
- All requests HTTPS; responses `application/json`.

Sources: https://docs.payroc.com/getting-started , https://docs.payroc.com/api/postman-collection ,
https://docs.payroc.com/essentials/hosted-fields/authenticate-your-session ,
https://docs.payroc.com/test/test-your-integration/payroc-cloud-simulator/send-test-requests-to-our-gateway ,
https://packagist.org/packages/payroc/payroc-sdk-php , https://docs.payroc.com/api/payroc-sd-ks-beta

## 3. Payroc Cloud – payment instructions

Concept: semi-integrated. POS (our PHP server) sends an instruction to the gateway addressed to a device
**serial number**; the Payroc App / device picks it up. Supported: Android devices running Payroc App
(POS same or separate device), non-Android Ingenico and ID TECH (POS on separate device).
Device setup guides: `/guides/payments/payroc-cloud/device-setup/{android-same-device|android-diff-device|ingenico|idtech}`.

### 3.1 Submit payment instruction
`POST {base}/devices/{serialNumber}/payment-instructions`  (operation "Submit payment instruction")

Headers:
- `Authorization: Bearer <token>`
- `Content-Type: application/json`
- `Idempotency-Key: <UUID v4>` – **required** (missing -> 400)

Path: `serialNumber` (string, required) – device serial number.

Body:
- `processingTerminalId` (string, 4–50, **required**) – e.g. `"1234001"`
- `order` (object, **required**)
  - `orderId` (string, 1–24, **required**, merchant-assigned)
  - `amount` (int64, **required**) – total in lowest denomination (**cents**). e.g. `4999` = $49.99
  - `currency` (string, **required**, ISO 4217, e.g. `"USD"`)
  - `description` (string, 0–1024)
  - `acceptPartialAmount` (bool, default false)
  - `breakdown` (object):
    - `subtotal` (int64; required for Level 2/3/CEDP)
    - `tip`: `type` = `percentage` | `fixedAmount` (required); `amount` (int64) for fixed, or `percentage` (<=100) – percentage applied after tax
    - `taxes[]`: `name` (1–64, required, validated against stored rate), `rate` (0–99.99999), `type` = `rate`
    - `surcharge`: `bypass` (bool; true removes surcharge fee)
    - `dualPricing`: `offered` (bool), `alternativeTender` = `card|cash|bankTransfer`
    - `cashbackAmount` (int64), `healthcareExpenses[]`
- `operator` (string, 0–50) – e.g. tech/cashier name
- `autoCapture` (bool) – true = sale + capture; false = pre-auth (status pending if terminal can't pre-auth)
- `processAsSale` (bool) – settle immediately, ignores autoCapture, cannot be adjusted afterwards
- `customizationOptions`:
  - `entryMethod` = `deviceRead` | `manualEntry` | `deviceReadOrManualEntry`
  - `ebtDetails` {`benefitCategory` cash|foodStamp, `withdrawal`}, `closedLoopOptions` {`type`: `mifare`}
- `customer` (billingAddress, shippingAddress, contactMethods[] {type email|phone|mobile|fax, value}, firstName, lastName, dateOfBirth, notificationLanguage, referenceNumber)
- `credentialOnFile` {`tokenize`, `secureTokenId`, `externalVault`, `mitAgreement`}
- `ipAddress` {`type` ipv4|ipv6, `value`}

Tip handling: either let the **gateway/terminal settings** prompt for tip on the device (test case 1:
"gateway-configured options (surcharging, tips, tax)"), or override in request via `order.breakdown.tip`
(test case 2 uses a 10% tip and tax `TAX10`). Enabling the on-device tip prompt is a gateway setting changed
by Payroc ("Some cases need gateway settings changed, such as enabling a tip prompt").
- **`autoCloseout`: not a field on this endpoint – UNCONFIRMED/does not exist.** Batch close timing is set in
  Merchant Portal terminal settings; gateway settles within an hour after batch close.
- No flat `tipAmount` field.

Example request:
```json
{
  "processingTerminalId": "1234001",
  "operator": "Jane",
  "order": { "orderId": "OrderRef6543", "amount": 4999, "currency": "USD" },
  "customizationOptions": { "entryMethod": "deviceRead" },
  "autoCapture": true
}
```

Response **202 Accepted**:
```json
{
  "paymentInstructionId": "a37439165d134678a9100ebba3b29597",
  "status": "inProgress",
  "link": { "rel": "self", "method": "GET",
            "href": "https://api.payroc.com/v1/payment-instructions/a37439165d134678a9100ebba3b29597" }
}
```
- `paymentInstructionId` string 1–36
- `status` enum: `inProgress` | `completed` | `failure` | `canceled`
- `errorMessage` only when `status = failure`

### 3.2 Poll status
`GET {base}/payment-instructions/{paymentInstructionId}` -> 200
- Long-poll: "The gateway waits up to one minute for the status to change before responding." If still
  `inProgress`, GET again; **do not send a new request until the previous one returns** (set PHP/cURL
  timeout > 60 s, e.g. 75 s; or run polling in a background worker, not in the web request).
- Completed example:
```json
{ "status": "completed", "paymentInstructionId": "a37439165d134678a9100ebba3b29597",
  "link": { "rel": "payment", "method": "GET", "href": "https://api.payroc.com/v1/payments/M2MJOG6O2Y" } }
```
- Take `paymentId` from `link.href` where `rel = "payment"`.
- Errors: 400/401/403/404/406/500.

### 3.3 Get resulting payment
`GET {base}/payments/{paymentId}`
- Fields: `paymentId`, `processingTerminalId`, `order` (orderId, dateTime, amount, currency, breakdown…),
  `card` (type, entryMethod, cardNumber (masked), expiryDate, secureToken, securityChecks), `customer`,
  `refunds[]`, `supportedOperations`, `customFields`, `operator`,
  `transactionResult` { `type`, `status`, `approvalCode`, `authorizedAmount`, `currency`,
  `responseCode` (example `"A"`), `responseMessage`, `cardSchemeReferenceId` }.
- Full enums of `transactionResult.status` / `responseCode` / `supportedOperations`: **UNCONFIRMED**
  (examples seen: responseCode `A` = approved; status `reversal` after a reverse). Treat approval as
  instruction `completed` AND responseCode `A`; verify enum list in API reference.
- Search: `GET {base}/payments` (list with filters).

### 3.4 Cancel pending instruction
`DELETE {base}/payment-instructions/{paymentInstructionId}`
- Only while `status = inProgress`.
- 204 No Content on success.
- 409 `Cannot be canceled` (`type: https://docs.payroc.com/api/errors#cannot-be-canceled`, e.g. "Completed instruction cannot be canceled"; includes link to the payment).

Sources:
- https://docs.payroc.com/essentials/payroc-cloud
- https://docs.payroc.com/essentials/payroc-cloud/run-a-sale.md
- https://docs.payroc.com/guides/take-payments/payroc-cloud/run-a-sale
- https://docs.payroc.com/api/schema/payroc-cloud/payment-instructions/submit
- https://docs.payroc.com/api/schema/payroc-cloud/payment-instructions/retrieve
- https://docs.payroc.com/api/schema/payroc-cloud/payment-instructions/delete
- https://docs.payroc.com/api/schema/card-payments/payments/retrieve.md

## 4. Refunds and reversals

### 4.1 Unreferenced refund on device (Cloud)
`POST {base}/devices/{serialNumber}/refund-instructions`  (Idempotency-Key required)
Body: `processingTerminalId` (req), `operator`, `order` { `orderId` (1–24, req), `amount` (int64 cents, req),
`currency` (req), `description` (0–1024, listed as required) }, `customizationOptions` {entryMethod, ebtDetails,
closedLoopOptions}, `customer`, `ipAddress`.
Response 202: `refundInstructionId` (1–36), `status` (`inProgress|completed|failure|canceled`), `errorMessage`, `link`.
- Poll: `GET {base}/refund-instructions/{refundInstructionId}` (same 1-minute long-poll); link gives `refundId`.
- Result: `GET {base}/refunds/{refundId}`.
- Cancel: `DELETE {base}/refund-instructions/{refundInstructionId}` (only while `inProgress`).

### 4.2 Referenced refund (server-to-gateway, no device)
`POST {base}/payments/{paymentId}/refund` (Idempotency-Key required). Use after batch closed.
Refund appears in payment's `refunds[]` (example amount shown negative, -4000). Request body fields:
**UNCONFIRMED** (likely `amount`, `description`, `operator` – check API reference).
Note: "If the payment is in an open batch, the gateway automatically cancels the payment when a refund is run on it."

### 4.3 Reverse (void) a payment
`POST {base}/payments/{paymentId}/reverse` (Idempotency-Key required)
- Payment must be in an **open batch**; removes it from the batch, no funds taken.
- Body (optional): `amount` (int64 cents; less than total = partial reversal; omit = full), `operator`.
- 200 returns payment object, `transactionResult.status` e.g. `reversal`.
- Related (paths **UNCONFIRMED**): Capture payment (for `pending` pre-auth), Adjust payment (tip/amount after auth), Reverse refund.

Sources:
- https://docs.payroc.com/api/schema/payroc-cloud/refund-instructions/submit
- https://docs.payroc.com/essentials/payroc-cloud/extend-your-solution/run-an-unreferenced-refund.md
- https://docs.payroc.com/essentials/payroc-cloud/extend-your-solution/run-a-referenced-refund.md
- https://docs.payroc.com/api/schema/card-payments/refunds/reverse

## 5. Errors, idempotency, rate limits

- Format: RFC 7807 problem details, content type `application/problem+json`; fields `type`, `title`,
  `status`, `detail`; optional `errors[]` (validation: `parameter`, `message`), `resource`, `instance`, `link`.
- `type` URIs: `https://docs.payroc.com/api/errors#<error-name>` (e.g. `#not-found`, `#idempotency-key-in-use`, `#cannot-be-canceled`).
- Example:
```json
{ "type": "https://docs.payroc.com/api/errors#not-found", "title": "Not found",
  "status": 404, "detail": "Resource not found", "resource": "account" }
```
- Status codes: 400 (bad request, capability/card type/currency not supported, idempotency key missing…),
  401 not authorized, 403 forbidden, 404 not found, 405 method not supported, 406 not acceptable,
  409 (cannot be canceled, cannot be modified, Idempotency-Key in use, resource already exists, duplicate unique reference…),
  413 payload too large, 415 unsupported media type, 500 API/internal error.
- Idempotency: unique `Idempotency-Key` (UUID v4) required on **all POST and PATCH**. Missing -> 400
  "Idempotent-key header missing". Same key with different request -> 409 "Idempotency-Key in use"
  ("'Idempotency-Key' is already in use against a different request"). On 500, docs say retry **with the
  same** idempotency key. Key retention window: **UNCONFIRMED**. 409 "Resource already exists" includes a
  `link` to the existing resource (useful for safe retries).
- Rate limits / 429: **UNCONFIRMED** (not mentioned on the Errors page).

Sources: https://docs.payroc.com/api/errors , submit/reverse schema pages above.

## 6. Test / sandbox specifics

Card test values (Payroc Cloud test page):
| Scheme | Number | Verification |
|---|---|---|
| Visa | 4761 7300 0000 0011 | Online only |
| Mastercard | 5413 3300 8960 4111 | Online only (also listed as online/offline – table is inconsistent) |
| Visa | 4761 7310 0000 0043 | Online or offline |

Amount endings (gateway test environment): `..01` declined (e.g. 501), `..02` referral (1002),
`..03` CVV failure (1403), anything else authorized (4541).

**Payroc Cloud Simulator** (virtual device, no physical terminal/test card needed):
- Web app at `https://cloud.uat.payroc.com`. Enter processing terminal ID + **Payroc App API key**,
  Save, then **Copy S/N and Continue** – each browser tab gets a mock serial number to use as `{serialNumber}`.
- Use Submit Payment Instruction / Submit Refund Instruction against it; cancel optional.
- Sessions expire after 15 min inactivity; closing the tab deletes the session. Logs: Simulator Details > Download log file.
- Simulator amounts – entry method: $1.00 EMV signature; $3.00 EMV PIN; $8.00 EMV fallback; >$8.00 EMV no CVM;
  $4.00 swipe no CVM; $5.00 swipe signature; $6.00 contactless; $7.00 contactless invalid tags.
- Simulator behaviour cents (sale only, add to amount): `.99` cardholder cancels on device; `.09` or `.66`
  device immediately reverses sale; `.59` merchant surcharge (needs Allow Surcharges + Disclose Fee settings).
  e.g. $6.59 = contactless + surcharge.

Integration test cases (public list):
1. Payment instruction using gateway-configured options (surcharge, tips, tax) -> POST instruction, GET until `completed`, GET payment.
2. Payment instruction overriding gateway settings (10% tip, tax `TAX10`) -> same flow.
3. Card-not-present refund via refund instruction -> POST refund-instructions, GET until `completed`, GET refund.
If an instruction ends `failed`/`canceled`, contact Payroc Integration Engineer. Also: test error scenarios,
every card type accepted, and that Bearer tokens are refreshed correctly. Contact: payroc-integrations@payroc.com.
Formal certification sign-off procedure: **UNCONFIRMED** (not public on the pages read).

Sources:
- https://docs.payroc.com/test/test-your-integration/payroc-cloud
- https://docs.payroc.com/test/test-your-integration/pay-by-cloud
- https://docs.payroc.com/test/test-your-integration/payroc-cloud-simulator
- https://docs.payroc.com/test/test-your-integration/payroc-cloud-simulator/test-transaction-values
- https://docs.payroc.com/test/test-your-integration/payroc-cloud-simulator/send-test-requests-to-our-gateway

## 7. Webhooks / event subscriptions

- Event subscriptions exist (CloudEvents format: specversion, type, version, source, id, time,
  datacontenttype, data; retried up to 5 times if endpoint doesn't return 200).
- Listed event types are boarding only: `processingAccount.riskStatus.changed`,
  `processingAccount.signature.signed`, `processingAccount.status.changed`, `terminalOrder.status.changed`.
- **No payment / payment-instruction / refund events** -> status must be obtained by long-polling (section 3.2).
- Webhook signature/verification method: **UNCONFIRMED**.

Sources: https://docs.payroc.com/knowledge/events/events-list , https://docs.payroc.com/api/schema/event-subscriptions/overview

## Implementation notes for PHP (derived, not from docs)
- Cache token ~55 min; refresh on 401 once.
- New UUID v4 per POST; store it with the NailFlow order so a retry after timeout/500 reuses the same key.
- `orderId` max 24 chars – use a compact NailFlow ticket id.
- Poll in a background job/CLI loop with cURL timeout ~75 s; UI polls our own DB.
- Store `paymentInstructionId`, `paymentId`, `transactionResult.status/responseCode/approvalCode`, masked card.
- Same-day void -> `/payments/{id}/reverse`; after batch close -> `/payments/{id}/refund`.
