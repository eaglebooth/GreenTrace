# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing
import json


class GreenTrace(gl.Contract):
    company_count: u256
    company_name: TreeMap[u256, str]
    company_wallet: TreeMap[u256, str]
    company_industry: TreeMap[u256, str]
    company_facility_url: TreeMap[u256, str]
    company_baseline_tons: TreeMap[u256, u256]
    company_status: TreeMap[u256, str]
    company_credit_balance: TreeMap[u256, u256]
    company_total_verified_reduction: TreeMap[u256, u256]

    report_count: u256
    report_company_id: TreeMap[u256, u256]
    report_period: TreeMap[u256, str]
    report_self_url: TreeMap[u256, str]
    report_satellite_url: TreeMap[u256, str]
    report_sensor_url: TreeMap[u256, str]
    report_requested_credits: TreeMap[u256, u256]
    report_status: TreeMap[u256, str]
    report_awarded_credits: TreeMap[u256, u256]
    report_greenwash_risk: TreeMap[u256, u256]
    report_ecology_score: TreeMap[u256, u256]
    report_ai_reason: TreeMap[u256, str]

    total_credits_issued: u256
    transfer_count: u256
    transfer_from_company: TreeMap[u256, u256]
    transfer_to_wallet: TreeMap[u256, str]
    transfer_amount: TreeMap[u256, u256]

    def __init__(self):
        self.company_count = u256(0)
        self.report_count = u256(0)
        self.total_credits_issued = u256(0)
        self.transfer_count = u256(0)

    def clamp_score(self, value: typing.Any) -> u256:
        parsed = int(value)
        if parsed < 0:
            return u256(0)
        if parsed > 100:
            return u256(100)
        return u256(parsed)

    def truncate(self, value: str, limit: u256) -> str:
        if len(value) > int(limit):
            return value[: int(limit)] + "...[TRUNCATED]"
        return value

    @gl.public.write
    def register_company(
        self,
        name: str,
        wallet: str,
        industry: str,
        facility_url: str,
        baseline_tons: u256,
    ) -> typing.Any:
        if len(name) == 0:
            return "INVALID_NAME"
        if len(wallet) == 0:
            return "INVALID_WALLET"
        if len(industry) == 0:
            return "INVALID_INDUSTRY"
        if len(facility_url) < 4 or facility_url[:4] != "http":
            return "INVALID_FACILITY_URL"
        if baseline_tons == u256(0):
            return "INVALID_BASELINE"

        company_id = self.company_count
        self.company_name[company_id] = name
        self.company_wallet[company_id] = wallet
        self.company_industry[company_id] = industry
        self.company_facility_url[company_id] = facility_url
        self.company_baseline_tons[company_id] = baseline_tons
        self.company_status[company_id] = "ACTIVE"
        self.company_credit_balance[company_id] = u256(0)
        self.company_total_verified_reduction[company_id] = u256(0)
        self.company_count = company_id + u256(1)
        return company_id

    @gl.public.write
    def submit_report(
        self,
        company_id: u256,
        period: str,
        self_report_url: str,
        satellite_url: str,
        sensor_url: str,
        requested_credits: u256,
    ) -> typing.Any:
        if company_id >= self.company_count:
            return "INVALID_COMPANY_ID"
        if self.company_status[company_id] != "ACTIVE":
            return "COMPANY_NOT_ACTIVE"
        if len(period) == 0:
            return "INVALID_PERIOD"
        if len(self_report_url) < 4 or self_report_url[:4] != "http":
            return "INVALID_SELF_REPORT_URL"
        if len(satellite_url) < 4 or satellite_url[:4] != "http":
            return "INVALID_SATELLITE_URL"
        if len(sensor_url) < 4 or sensor_url[:4] != "http":
            return "INVALID_SENSOR_URL"
        if requested_credits == u256(0):
            return "INVALID_REQUESTED_CREDITS"

        report_id = self.report_count
        self.report_company_id[report_id] = company_id
        self.report_period[report_id] = period
        self.report_self_url[report_id] = self_report_url
        self.report_satellite_url[report_id] = satellite_url
        self.report_sensor_url[report_id] = sensor_url
        self.report_requested_credits[report_id] = requested_credits
        self.report_status[report_id] = "PENDING_AUDIT"
        self.report_awarded_credits[report_id] = u256(0)
        self.report_greenwash_risk[report_id] = u256(0)
        self.report_ecology_score[report_id] = u256(0)
        self.report_ai_reason[report_id] = ""
        self.report_count = report_id + u256(1)
        return report_id

    @gl.public.write
    def audit_report(self, report_id: u256) -> str:
        if report_id >= self.report_count:
            return "INVALID_REPORT_ID"
        if self.report_status[report_id] != "PENDING_AUDIT":
            return "ALREADY_AUDITED"

        company_id = self.report_company_id[report_id]
        if company_id >= self.company_count:
            return "INVALID_COMPANY"
        if self.company_status[company_id] != "ACTIVE":
            return "COMPANY_NOT_ACTIVE"

        company_name = self.company_name[company_id]
        industry = self.company_industry[company_id]
        facility_url = self.company_facility_url[company_id]
        baseline = self.company_baseline_tons[company_id]
        period = self.report_period[report_id]
        self_report_url = self.report_self_url[report_id]
        satellite_url = self.report_satellite_url[report_id]
        sensor_url = self.report_sensor_url[report_id]
        requested_credits = self.report_requested_credits[report_id]

        def run_audit() -> str:
            try:
                facility_resp = gl.nondet.web.render(facility_url, media_type="html")
                report_resp = gl.nondet.web.render(self_report_url, media_type="html")
                satellite_resp = gl.nondet.web.render(satellite_url, media_type="html")
                sensor_resp = gl.nondet.web.render(sensor_url, media_type="html")

                facility_content = self.truncate(facility_resp.body.decode("utf-8"), u256(1400))
                report_content = self.truncate(report_resp.body.decode("utf-8"), u256(2200))
                satellite_content = self.truncate(satellite_resp.body.decode("utf-8"), u256(1400))
                sensor_content = self.truncate(sensor_resp.body.decode("utf-8"), u256(1400))
            except Exception:
                return json.dumps({"error": "WEB_RENDER_FAILED"}, sort_keys=True, separators=(",", ":"))

            prompt = f"""
You are GreenTrace, a GenLayer carbon-credit audit jury.

COMPANY: {company_name}
INDUSTRY: {industry}
REPORTING PERIOD: {period}
BASELINE EMISSIONS TONS CO2E: {baseline}
REQUESTED CARBON CREDITS: {requested_credits}

FACILITY PAGE:
{facility_content}

COMPANY SELF-REPORTED ENVIRONMENTAL CLAIM:
{report_content}

SATELLITE OR LAND-USE EVIDENCE:
{satellite_content}

PUBLIC SENSOR OR POLLUTION EVIDENCE:
{sensor_content}

TASK:
Compare the voluntary report against independent web evidence. Decide whether
the company deserves tradable carbon credits, reduced credits, review, or rejection.
Check for greenwashing, inflated tree-planting claims, pollution contradicting
the report, and whether reductions have real ecological value.

SCORING:
- evidence_alignment_score 0-100: consistency between report and independent evidence.
- ecology_score 0-100: real ecological benefit and durability.
- greenwash_risk 0-100: higher means more likely deceptive or unverifiable.
- verified_reduction_tons: conservative whole-number estimate of credible CO2e reduction.
- credits_awarded: whole-number credits, never above requested credits.

DECISION:
- CERTIFIED if alignment >= 75, ecology >= 70, greenwash_risk <= 25.
- REDUCED if alignment >= 55 and greenwash_risk <= 50.
- NEEDS_REVIEW if evidence is mixed or incomplete.
- REJECTED if claims are contradicted, unverifiable, or greenwash_risk > 70.

Respond with ONLY strict JSON:
{{
  "decision": "CERTIFIED" | "REDUCED" | "NEEDS_REVIEW" | "REJECTED",
  "evidence_alignment_score": 0,
  "ecology_score": 0,
  "greenwash_risk": 0,
  "verified_reduction_tons": 0,
  "credits_awarded": 0,
  "reason": "one concise sentence"
}}
"""
            return gl.nondet.exec_prompt(prompt)

        consensus = gl.eq_principle.strict_eq(run_audit)
        try:
            data = json.loads(consensus)
        except json.JSONDecodeError:
            return "INVALID_AI_RESPONSE"

        if "error" in data:
            return "WEB_RENDER_FAILED"

        decision = str(data.get("decision", "")).upper()
        if decision not in ["CERTIFIED", "REDUCED", "NEEDS_REVIEW", "REJECTED"]:
            return "INVALID_DECISION"

        greenwash_risk = self.clamp_score(data.get("greenwash_risk", 100))
        ecology_score = self.clamp_score(data.get("ecology_score", 0))
        awarded = u256(int(data.get("credits_awarded", 0)))
        verified_reduction = u256(int(data.get("verified_reduction_tons", 0)))

        if awarded > requested_credits:
            awarded = requested_credits
        if decision == "REJECTED" or decision == "NEEDS_REVIEW":
            awarded = u256(0)

        self.report_status[report_id] = decision
        self.report_greenwash_risk[report_id] = greenwash_risk
        self.report_ecology_score[report_id] = ecology_score
        self.report_awarded_credits[report_id] = awarded
        self.report_ai_reason[report_id] = consensus

        if awarded > u256(0):
            self.company_credit_balance[company_id] = self.company_credit_balance[company_id] + awarded
            self.company_total_verified_reduction[company_id] = self.company_total_verified_reduction[company_id] + verified_reduction
            self.total_credits_issued = self.total_credits_issued + awarded

        return decision

    @gl.public.write
    def transfer_credits(self, company_id: u256, to_wallet: str, amount: u256) -> str:
        if company_id >= self.company_count:
            return "INVALID_COMPANY_ID"
        if len(to_wallet) == 0:
            return "INVALID_RECIPIENT"
        if amount == u256(0):
            return "INVALID_AMOUNT"
        balance = self.company_credit_balance[company_id]
        if amount > balance:
            return "INSUFFICIENT_CREDITS"

        self.company_credit_balance[company_id] = balance - amount
        transfer_id = self.transfer_count
        self.transfer_from_company[transfer_id] = company_id
        self.transfer_to_wallet[transfer_id] = to_wallet
        self.transfer_amount[transfer_id] = amount
        self.transfer_count = transfer_id + u256(1)
        return "TRANSFERRED"

    @gl.public.view
    def get_company_count(self) -> u256:
        return self.company_count

    @gl.public.view
    def get_report_count(self) -> u256:
        return self.report_count

    @gl.public.view
    def get_market_stats(self) -> str:
        data = {
            "company_count": str(self.company_count),
            "report_count": str(self.report_count),
            "total_credits_issued": str(self.total_credits_issued),
            "transfer_count": str(self.transfer_count),
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_company(self, company_id: u256) -> str:
        if company_id >= self.company_count:
            return json.dumps({"error": "INVALID_COMPANY_ID"}, sort_keys=True, separators=(",", ":"))
        data = {
            "baseline_tons": str(self.company_baseline_tons[company_id]),
            "credit_balance": str(self.company_credit_balance[company_id]),
            "facility_url": self.company_facility_url[company_id],
            "industry": self.company_industry[company_id],
            "name": self.company_name[company_id],
            "status": self.company_status[company_id],
            "total_verified_reduction": str(self.company_total_verified_reduction[company_id]),
            "wallet": self.company_wallet[company_id],
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_report(self, report_id: u256) -> str:
        if report_id >= self.report_count:
            return json.dumps({"error": "INVALID_REPORT_ID"}, sort_keys=True, separators=(",", ":"))
        data = {
            "awarded_credits": str(self.report_awarded_credits[report_id]),
            "company_id": str(self.report_company_id[report_id]),
            "ecology_score": str(self.report_ecology_score[report_id]),
            "greenwash_risk": str(self.report_greenwash_risk[report_id]),
            "period": self.report_period[report_id],
            "reason": self.report_ai_reason[report_id],
            "requested_credits": str(self.report_requested_credits[report_id]),
            "satellite_url": self.report_satellite_url[report_id],
            "self_report_url": self.report_self_url[report_id],
            "sensor_url": self.report_sensor_url[report_id],
            "status": self.report_status[report_id],
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))
