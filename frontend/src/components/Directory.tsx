"use client";
import Link from "next/link";
import { ArrowRight, RefreshCw } from "lucide-react";
import { useState } from "react";
import { readContract } from "@/lib/genlayer";

export function Directory({ kind }: { kind: "companies" | "reports" }) {
  const address = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";
  const [rows, setRows] = useState<Record<string, string>[]>([]);
  const [message, setMessage] = useState(address ? "Ready to sync live state." : "GreenTrace V2 deployment pending.");
  const [busy, setBusy] = useState(false);
  async function sync() {
    if (!address) return;
    setBusy(true);
    const count = await readContract(kind === "companies" ? "get_company_count" : "get_report_count", [], address);
    if (!count.success) { setMessage(count.error || "Read failed"); setBusy(false); return; }
    const total = Number(count.data || 0);
    const calls = await Promise.all(Array.from({ length: total }, (_, id) => readContract(kind === "companies" ? "get_company" : "get_report", [id], address)));
    const parsed = calls.flatMap((result) => { try { return result.success && typeof result.data === "string" ? [JSON.parse(result.data)] : []; } catch { return []; } });
    setRows(parsed);
    setMessage(total ? `Synced ${parsed.length} live ${kind}.` : `No ${kind} recorded on V2 yet.`);
    setBusy(false);
  }
  return <section className="section"><div className="split-actions"><span className="notice">{message}</span><button className="ghost-button" onClick={sync} disabled={!address || busy}><RefreshCw size={16}/>{busy ? "Syncing" : "Sync contract"}</button></div>{rows.length === 0 ? <div className="empty" style={{ marginTop: 28 }}><h2>No fabricated records.</h2><p>Only records returned by the deployed contract appear here.</p></div> : <div className="record-list" style={{ marginTop: 28 }}>{rows.map((row, id) => kind === "companies" ? <div className="record-row" key={id}><strong>#{id}</strong><div><strong>{row.name}</strong><small>{row.owner}</small></div><span>{row.status}</span><span>{row.credit_balance} credits</span><span/></div> : <Link className="record-row" href={`/reports/${id}`} key={id}><strong>#{id}</strong><div><strong>{row.period}</strong><small>Company #{row.company_id}</small></div><span>{row.status}</span><span>{row.decision}</span><ArrowRight size={16}/></Link>)}</div>}</section>;
}
