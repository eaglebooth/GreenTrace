"use client";

import { motion } from "framer-motion";
import {
  ArrowRight,
  BadgeCheck,
  Factory,
  Leaf,
  LineChart,
  RadioTower,
  Satellite,
  SearchCheck,
  Sprout,
  Wallet,
} from "lucide-react";
import { useMemo, useState } from "react";
import { connectWallet, readContract, writeContract } from "@/lib/genlayer";

type FormState = {
  name: string;
  wallet: string;
  industry: string;
  facilityUrl: string;
  baseline: string;
  period: string;
  selfReportUrl: string;
  satelliteUrl: string;
  sensorUrl: string;
  requestedCredits: string;
  reportId: string;
  transferWallet: string;
  transferAmount: string;
};

const defaultForm: FormState = {
  name: "Evergreen Textile Cooperative",
  wallet: "0x0000000000000000000000000000000000000001",
  industry: "Low-impact textile manufacturing",
  facilityUrl: "https://example.com/facility-evergreen",
  baseline: "8200",
  period: "Q2 2026",
  selfReportUrl: "https://example.com/evergreen-q2-sustainability",
  satelliteUrl: "https://example.com/evergreen-satellite-canopy",
  sensorUrl: "https://example.com/public-air-sensor-evergreen",
  requestedCredits: "420",
  reportId: "0",
  transferWallet: "0x0000000000000000000000000000000000000002",
  transferAmount: "25",
};

const steps = [
  {
    icon: Factory,
    title: "Register Facility",
    text: "Company identity, industry context, facility page, and baseline emissions are stored on-chain.",
  },
  {
    icon: Satellite,
    title: "Attach Evidence",
    text: "Reports are submitted with independent satellite, land-use, sensor, or investigation URLs.",
  },
  {
    icon: SearchCheck,
    title: "GenLayer Audit",
    text: "Validators compare claims with live web evidence and score greenwashing risk.",
  },
  {
    icon: BadgeCheck,
    title: "Mint Dynamic Credits",
    text: "Only verified reductions become transferable carbon credits in the contract ledger.",
  },
];

function shortAddress(value: unknown) {
  const text = String(value || "");
  if (text.length < 12) return text;
  return `${text.slice(0, 6)}...${text.slice(-4)}`;
}

export default function Home() {
  const [form, setForm] = useState<FormState>(defaultForm);
  const [wallet, setWallet] = useState("");
  const [status, setStatus] = useState("Ready. Configure a contract address after Studio deployment.");
  const [busy, setBusy] = useState(false);
  const [log, setLog] = useState("GreenTrace console\n- Awaiting wallet connection\n- Contract mode: real genlayer-js calls");
  const [stats, setStats] = useState({
    companies: "0",
    reports: "0",
    credits: "0",
    transfers: "0",
  });

  const configured = useMemo(
    () => Boolean(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS),
    [],
  );

  function updateField(key: keyof FormState, value: string) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function appendLog(line: string) {
    setLog((current) => `${current}\n- ${line}`);
  }

  async function handleConnect() {
    const result = await connectWallet();
    if (result.success) {
      const account = String(result.data);
      setWallet(account);
      updateField("wallet", account);
      setStatus(`Wallet connected: ${shortAddress(account)}`);
      appendLog(`wallet ${shortAddress(account)} connected`);
    } else {
      setStatus(result.error || "Wallet connection failed");
      appendLog(result.error || "wallet connection failed");
    }
  }

  async function refreshStats() {
    const result = await readContract("get_market_stats");
    if (!result.success) {
      appendLog(result.error || "market stats unavailable");
      return;
    }
    try {
      const parsed = JSON.parse(String(result.data));
      setStats({
        companies: String(parsed.company_count || "0"),
        reports: String(parsed.report_count || "0"),
        credits: String(parsed.total_credits_issued || "0"),
        transfers: String(parsed.transfer_count || "0"),
      });
      appendLog("market stats refreshed from contract");
    } catch {
      appendLog("market stats returned non-json data");
    }
  }

  async function registerCompany() {
    setBusy(true);
    setStatus("Registering company on GreenTrace...");
    const result = await writeContract("register_company", [
      form.name,
      form.wallet,
      form.industry,
      form.facilityUrl,
      BigInt(form.baseline || "0"),
    ]);
    setBusy(false);
    setStatus(result.success ? `Company registered. Tx ${shortAddress(result.hash)}` : result.error || "Registration failed");
    appendLog(result.success ? "company registration finalized" : result.error || "registration failed");
    if (result.success) await refreshStats();
  }

  async function submitReport() {
    setBusy(true);
    setStatus("Submitting emissions report...");
    const result = await writeContract("submit_report", [
      BigInt(0),
      form.period,
      form.selfReportUrl,
      form.satelliteUrl,
      form.sensorUrl,
      BigInt(form.requestedCredits || "0"),
    ]);
    setBusy(false);
    setStatus(result.success ? `Report submitted. Tx ${shortAddress(result.hash)}` : result.error || "Report submission failed");
    appendLog(result.success ? "report submitted for AI audit" : result.error || "report submission failed");
    if (result.success) await refreshStats();
  }

  async function runAudit() {
    setBusy(true);
    setStatus("Running GenLayer AI carbon audit...");
    const result = await writeContract("audit_report", [BigInt(form.reportId || "0")]);
    setBusy(false);
    setStatus(result.success ? `Audit finalized. Result ${String(result.data || result.status || "finalized")}` : result.error || "Audit failed");
    appendLog(result.success ? "AI audit consensus finalized" : result.error || "AI audit failed");
    if (result.success) await refreshStats();
  }

  async function transferCredits() {
    setBusy(true);
    setStatus("Transferring certified credits...");
    const result = await writeContract("transfer_credits", [
      BigInt(0),
      form.transferWallet,
      BigInt(form.transferAmount || "0"),
    ]);
    setBusy(false);
    setStatus(result.success ? `Credits transferred. Tx ${shortAddress(result.hash)}` : result.error || "Transfer failed");
    appendLog(result.success ? "credit transfer finalized" : result.error || "credit transfer failed");
    if (result.success) await refreshStats();
  }

  return (
    <main className="page">
      <nav className="nav">
        <a className="brand" href="#top">
          <span className="brand-mark"><Leaf size={25} /></span>
          GreenTrace
        </a>
        <div className="nav-links">
          <a href="#how">How it works</a>
          <a href="#audit">AI audit</a>
          <a href="#market">Credit ledger</a>
        </div>
        <button className="ghost-button" onClick={handleConnect} type="button">
          <Wallet size={18} />
          {wallet ? shortAddress(wallet) : "Connect wallet"}
        </button>
      </nav>

      <section className="hero" id="top">
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <span className="badge"><Sprout size={16} /> GenLayer-native carbon audits</span>
          <h1>
            Carbon credits that breathe with <span>real evidence.</span>
          </h1>
          <p>
            GreenTrace reads environmental reports, satellite pages, public sensor data,
            and local evidence inside an Intelligent Contract before certifying tradable credits.
          </p>
          <div className="hero-actions">
            <a className="pill-button" href="#audit">
              Start audit flow <ArrowRight size={18} />
            </a>
            <button className="ghost-button" onClick={refreshStats} type="button">
              Refresh ledger <LineChart size={18} />
            </button>
          </div>
        </motion.div>

        <motion.div className="canopy" initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.7, delay: 0.1 }}>
          <div className="river-card">
            <div className="river-row">
              <span className="brand-mark"><RadioTower size={24} /></span>
              <div>
                <strong>Independent evidence alignment</strong>
                <span>Satellite + sensor + report cross-check</span>
              </div>
              <strong>74%</strong>
            </div>
            <div className="meter"><div /></div>
          </div>
        </motion.div>
      </section>

      <section className="section" id="how">
        <div className="section-heading">
          <h2>How GreenTrace works</h2>
          <p>
            The app turns noisy climate claims into a bounded on-chain state machine,
            where AI consensus decides whether credits are certified, reduced, reviewed, or rejected.
          </p>
        </div>
        <div className="audit-lane">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <article className="lane-step" key={step.title}>
                <Icon size={32} />
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="workspace" id="audit">
        <div className="section">
          <div className="section-heading">
            <h2>Live audit console</h2>
            <p>
              These controls call the deployed GreenTrace contract through genlayer-js once
              `NEXT_PUBLIC_CONTRACT_ADDRESS` is set.
            </p>
          </div>

          <div className="console-shell">
            <div className="panel">
              <h3>Company profile</h3>
              <p>Register the emitting facility before submitting a carbon-credit report.</p>
              <div className="field-grid">
                <div className="field">
                  <label>Company</label>
                  <input value={form.name} onChange={(event) => updateField("name", event.target.value)} />
                </div>
                <div className="field-grid two">
                  <div className="field">
                    <label>Wallet</label>
                    <input value={form.wallet} onChange={(event) => updateField("wallet", event.target.value)} />
                  </div>
                  <div className="field">
                    <label>Baseline tons CO2e</label>
                    <input value={form.baseline} onChange={(event) => updateField("baseline", event.target.value)} />
                  </div>
                </div>
                <div className="field">
                  <label>Industry</label>
                  <input value={form.industry} onChange={(event) => updateField("industry", event.target.value)} />
                </div>
                <div className="field">
                  <label>Facility URL</label>
                  <input value={form.facilityUrl} onChange={(event) => updateField("facilityUrl", event.target.value)} />
                </div>
              </div>
              <div className="form-actions">
                <button className="pill-button" disabled={busy} onClick={registerCompany} type="button">
                  Register facility <ArrowRight size={18} />
                </button>
              </div>
            </div>

            <div className="fresh-board" id="market">
              <span className="badge"><Leaf size={16} /> On-chain carbon ledger</span>
              <div className="board-grid">
                <div className="metric"><strong>{stats.companies}</strong><span>companies</span></div>
                <div className="metric"><strong>{stats.reports}</strong><span>reports</span></div>
                <div className="metric"><strong>{stats.credits}</strong><span>credits issued</span></div>
                <div className="metric"><strong>{stats.transfers}</strong><span>transfers</span></div>
              </div>
              <div className="log">{log}</div>
            </div>
          </div>

          <div className="console-shell" style={{ marginTop: 20 }}>
            <div className="panel">
              <h3>Evidence packet</h3>
              <p>Submit the company report and two independent evidence sources for AI validation.</p>
              <div className="field-grid">
                <div className="field-grid two">
                  <div className="field">
                    <label>Period</label>
                    <input value={form.period} onChange={(event) => updateField("period", event.target.value)} />
                  </div>
                  <div className="field">
                    <label>Requested credits</label>
                    <input value={form.requestedCredits} onChange={(event) => updateField("requestedCredits", event.target.value)} />
                  </div>
                </div>
                <div className="field">
                  <label>Company report URL</label>
                  <input value={form.selfReportUrl} onChange={(event) => updateField("selfReportUrl", event.target.value)} />
                </div>
                <div className="field">
                  <label>Satellite evidence URL</label>
                  <input value={form.satelliteUrl} onChange={(event) => updateField("satelliteUrl", event.target.value)} />
                </div>
                <div className="field">
                  <label>Sensor evidence URL</label>
                  <input value={form.sensorUrl} onChange={(event) => updateField("sensorUrl", event.target.value)} />
                </div>
              </div>
              <div className="form-actions">
                <button className="pill-button" disabled={busy} onClick={submitReport} type="button">
                  Submit evidence <ArrowRight size={18} />
                </button>
              </div>
            </div>

            <div className="panel">
              <h3>AI certification</h3>
              <p>Run the GenLayer validator review, then optionally transfer certified credits.</p>
              <div className="field-grid">
                <div className="field-grid two">
                  <div className="field">
                    <label>Report ID</label>
                    <input value={form.reportId} onChange={(event) => updateField("reportId", event.target.value)} />
                  </div>
                  <div className="field">
                    <label>Transfer amount</label>
                    <input value={form.transferAmount} onChange={(event) => updateField("transferAmount", event.target.value)} />
                  </div>
                </div>
                <div className="field">
                  <label>Credit buyer wallet</label>
                  <input value={form.transferWallet} onChange={(event) => updateField("transferWallet", event.target.value)} />
                </div>
              </div>
              <div className="form-actions">
                <button className="pill-button" disabled={busy} onClick={runAudit} type="button">
                  Run AI carbon audit <SearchCheck size={18} />
                </button>
                <button className="icon-button" disabled={busy} onClick={transferCredits} type="button">
                  Transfer credits <ArrowRight size={18} />
                </button>
              </div>
              <div className="status-strip">
                <strong>{configured ? "Contract configured" : "Contract address pending"}</strong>
                <br />
                {status}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="final-band">
        <div className="final-inner">
          <div>
            <h2>Less greenwashing. More accountable climate finance.</h2>
            <p>
              GreenTrace makes carbon credits dynamic: every issuance is tied to public evidence,
              AI consensus, and a visible on-chain credit balance.
            </p>
          </div>
          <a className="pill-button" href="#audit">Open audit console <ArrowRight size={18} /></a>
        </div>
      </section>
    </main>
  );
}
