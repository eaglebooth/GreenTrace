# GreenTrace V2

GreenTrace is an evidence-bound carbon credit registry powered by GenLayer semantic
AI consensus. It compares company claims with trusted satellite and public sensor
sources before an independently finalized issuance reaches a wallet balance.

## Why GenLayer

Carbon additionality, ecological durability, source credibility, and greenwashing
risk require contextual judgment over live evidence. GreenTrace performs that
judgment inside an Intelligent Contract, then applies deterministic thresholds and
credit calculations on-chain.

## Security model

- Company ownership comes from `gl.message.sender_address`.
- Only the owner can submit a report for its company.
- Company self-reports must share the registered facility hostname.
- Satellite, sensor, and challenge URLs must use exact admin-approved hostnames.
- A company can submit only one report per period.
- Requested credits and verified reduction are bounded by the company baseline.
- Rich AI output uses `prompt_comparative`; contract code reapplies thresholds.
- Audit creates a proposal. Only the source admin can finalize issuance once.
- Finalized credits belong to wallet balances and support transfer and retirement.

## Lifecycle

```text
TRUST SOURCES -> REGISTER COMPANY -> SUBMIT REPORT -> PENDING_AUDIT
PENDING_AUDIT -> AUDIT_PROPOSED | NEEDS_REVIEW
AUDIT_PROPOSED -> CHALLENGE_PENDING -> CHALLENGE_RULING
AUDIT_PROPOSED | CHALLENGE_RULING -> FINALIZED
FINALIZED -> TRANSFER | RETIRE
```

## Frontend routes

- `/sources` trusted source governance
- `/companies` and `/companies/register`
- `/reports`, `/reports/new`, and report detail/action routes
- `/credits`, `/credits/transfer`, and `/credits/retire`
- `/how-it-works` complete lifecycle guide
- `/activity` real contract connection proof

The visual design preserves GreenTrace's original fresh green, mint, lime, sky, and
white palette while separating each contract action into a focused page.

## Local verification

```powershell
python -B -m unittest discover -s tests -v
cd frontend
npm install
npm run lint
npm run build
npm run dev -- -p 3038
```

## Deployment status

GreenTrace V2 is deployed on GenLayer Studio / Studionet at
`0x86fA47a8C0956866C95BB0BFb2a73D874C759119`. The frontend environment files
use this address for live reads and writes through `genlayer-js`.
