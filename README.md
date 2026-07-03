# GreenTrace

Dynamic carbon-credit certification for supply chains, powered by GenLayer AI audits against independent environmental evidence.

**One-line pitch:** GreenTrace dies without GenLayer because carbon-credit issuance depends on subjective AI comparison between company reports and live third-party evidence such as satellite pages, sensor data, and local environmental investigations.

## Submission Links

- **Live app:** https://greentrace-three.vercel.app
- **GitHub:** https://github.com/eaglebooth/GreenTrace
- **Contract:** `0x4CC22499aA6DC3fF7dEa1ba5551273dd235c9f68`

## Why GenLayer

Traditional carbon credits are easy to manipulate when companies self-report polished sustainability numbers. A deterministic contract can store a number, but it cannot decide whether a reforestation claim is real, whether pollution data contradicts the report, or whether a project is ecological value or greenwashing.

GreenTrace uses a GenLayer Intelligent Contract to:

- Register companies and their facility baseline emissions.
- Accept environmental reports plus independent satellite and public sensor URLs.
- Read those URLs on-chain with `gl.nondet.web.render`.
- Ask `gl.nondet.exec_prompt` to compare evidence, score greenwashing risk, and decide how many credits can be certified.
- Mint dynamic carbon credits into an on-chain ledger only after validator consensus.

## Project Structure

```text
GreenTrace/
  contracts/
    GreenTrace.py
  frontend/
    src/app/page.tsx
    src/lib/genlayer.ts
  scripts/deploy/deploy.ps1
  tests/test_contract_static.py
```

## Contract Flow

1. Deploy `GreenTrace.py` to GenLayer Studio.
2. Register a company with a wallet, industry, facility URL, and emissions baseline.
3. Submit a reporting period with:
   - company self-report URL
   - satellite / land-use evidence URL
   - public pollution sensor or environmental evidence URL
   - requested carbon credits
4. Run the AI audit.
5. Contract writes `CERTIFIED`, `REDUCED`, `NEEDS_REVIEW`, or `REJECTED`.
6. Awarded credits are added to the company credit balance and may be transferred.

## Pre-Deploy Verification

```powershell
python -m unittest discover -s tests
python -c "import ast; ast.parse(open('contracts/GreenTrace.py', encoding='utf-8').read())"
genlayer lint contracts/GreenTrace.py
```

## Frontend Setup

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev -- --port 3038
```

Set the deployed contract address:

```text
NEXT_PUBLIC_CONTRACT_ADDRESS=0x4CC22499aA6DC3fF7dEa1ba5551273dd235c9f68
NEXT_PUBLIC_NETWORK=studionet
NEXT_PUBLIC_GENLAYER_RPC=
```

## Demo Script

1. Connect wallet.
2. Register a sample company.
3. Submit an emissions report with three public evidence URLs.
4. Run the GenLayer AI audit.
5. Show the awarded credit balance, greenwash risk, and AI reason.

## Submission Assets

- GitHub: add after push.
- Live app: add after Vercel deploy.
- Video: record the full flow after contract address is configured.
