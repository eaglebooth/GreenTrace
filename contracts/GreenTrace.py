# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing
import json


class GreenTrace(gl.Contract):
    source_admin: Address
    trusted_source_hosts: DynArray[str]

    company_count: u256
    company_name: TreeMap[u256, str]
    company_owner: TreeMap[u256, Address]
    company_industry: TreeMap[u256, str]
    company_facility_url: TreeMap[u256, str]
    company_baseline_tons: TreeMap[u256, u256]
    company_status: TreeMap[u256, str]
    company_total_verified_reduction: TreeMap[u256, u256]

    report_count: u256
    report_company_id: TreeMap[u256, u256]
    report_period: TreeMap[u256, str]
    report_self_url: TreeMap[u256, str]
    report_satellite_url: TreeMap[u256, str]
    report_sensor_url: TreeMap[u256, str]
    report_challenge_url: TreeMap[u256, str]
    report_challenger: TreeMap[u256, Address]
    report_requested_credits: TreeMap[u256, u256]
    report_status: TreeMap[u256, str]
    report_decision: TreeMap[u256, str]
    report_proposed_credits: TreeMap[u256, u256]
    report_awarded_credits: TreeMap[u256, u256]
    report_alignment_score: TreeMap[u256, u256]
    report_greenwash_risk: TreeMap[u256, u256]
    report_ecology_score: TreeMap[u256, u256]
    report_verified_reduction: TreeMap[u256, u256]
    report_ai_reason: TreeMap[u256, str]
    report_finalized: TreeMap[u256, u256]

    wallet_credit_balance: TreeMap[Address, u256]
    total_credits_issued: u256
    total_credits_retired: u256
    transfer_count: u256
    transfer_from_wallet: TreeMap[u256, Address]
    transfer_to_wallet: TreeMap[u256, Address]
    transfer_amount: TreeMap[u256, u256]
    retirement_count: u256
    retirement_owner: TreeMap[u256, Address]
    retirement_amount: TreeMap[u256, u256]
    retirement_beneficiary: TreeMap[u256, str]
    retirement_reference: TreeMap[u256, str]

    def __init__(self):
        self.source_admin = gl.message.sender_address
        self.company_count = u256(0)
        self.report_count = u256(0)
        self.total_credits_issued = u256(0)
        self.total_credits_retired = u256(0)
        self.transfer_count = u256(0)
        self.retirement_count = u256(0)

    def _host(self, url: str) -> str:
        if not url.startswith("https://"):
            return ""
        rest = url[8:]
        host = rest.split("/", 1)[0].lower()
        if len(host) == 0 or "@" in host or ":" in host or "?" in host or "#" in host:
            return ""
        return host

    def _is_trusted_host(self, host: str) -> bool:
        i = u256(0)
        while i < u256(len(self.trusted_source_hosts)):
            if self.trusted_source_hosts[i] == host:
                return True
            i = i + u256(1)
        return False

    def _clamp_score(self, value: typing.Any) -> u256:
        try:
            parsed = int(value)
        except Exception:
            return u256(0)
        if parsed < 0:
            return u256(0)
        if parsed > 100:
            return u256(100)
        return u256(parsed)

    def _parse_audit(self, result: str) -> typing.Any:
        try:
            data = json.loads(result)
        except Exception:
            return None
        alignment = self._clamp_score(data.get("evidence_alignment_score", 0))
        ecology = self._clamp_score(data.get("ecology_score", 0))
        risk = self._clamp_score(data.get("greenwash_risk", 100))
        try:
            reduction_int = int(data.get("verified_reduction_tons", 0))
        except Exception:
            reduction_int = 0
        if reduction_int < 0:
            reduction_int = 0
        reason = str(data.get("reason", "No usable audit reason was returned."))[:900]
        return (alignment, ecology, risk, u256(reduction_int), reason)

    def _decision_for(self, alignment: u256, ecology: u256, risk: u256) -> str:
        if risk > u256(70) or alignment < u256(40):
            return "REJECTED"
        if alignment >= u256(75) and ecology >= u256(70) and risk <= u256(25):
            return "CERTIFIED"
        if alignment >= u256(55) and risk <= u256(50):
            return "REDUCED"
        return "NEEDS_REVIEW"

    def _credits_for(self, decision: str, requested: u256) -> u256:
        if decision == "CERTIFIED":
            return requested
        if decision == "REDUCED":
            return requested // u256(2)
        return u256(0)

    @gl.public.write
    def add_trusted_source_host(self, host: str) -> typing.Any:
        if gl.message.sender_address != self.source_admin:
            return "NOT_SOURCE_ADMIN"
        normalized = host.lower()
        if len(normalized) == 0 or "/" in normalized or ":" in normalized or "@" in normalized:
            return "INVALID_SOURCE_HOST"
        if self._is_trusted_host(normalized):
            return "SOURCE_ALREADY_TRUSTED"
        self.trusted_source_hosts.append(normalized)
        return "SOURCE_TRUSTED"

    @gl.public.write
    def register_company(self, name: str, industry: str, facility_url: str, baseline_tons: u256) -> typing.Any:
        if len(name) == 0 or len(name) > 120:
            return "INVALID_NAME"
        if len(industry) == 0 or len(industry) > 120:
            return "INVALID_INDUSTRY"
        if len(self._host(facility_url)) == 0:
            return "INVALID_FACILITY_URL"
        if baseline_tons == u256(0):
            return "INVALID_BASELINE"
        owner = gl.message.sender_address
        i = u256(0)
        while i < self.company_count:
            if self.company_owner[i] == owner:
                return "WALLET_ALREADY_REGISTERED"
            i = i + u256(1)

        company_id = self.company_count
        self.company_name[company_id] = name
        self.company_owner[company_id] = owner
        self.company_industry[company_id] = industry
        self.company_facility_url[company_id] = facility_url
        self.company_baseline_tons[company_id] = baseline_tons
        self.company_status[company_id] = "ACTIVE"
        self.company_total_verified_reduction[company_id] = u256(0)
        self.company_count = company_id + u256(1)
        return str(company_id)

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
        if self.company_owner[company_id] != gl.message.sender_address:
            return "NOT_COMPANY_OWNER"
        if self.company_status[company_id] != "ACTIVE":
            return "COMPANY_NOT_ACTIVE"
        if len(period) == 0 or len(period) > 80:
            return "INVALID_PERIOD"
        if requested_credits == u256(0) or requested_credits > self.company_baseline_tons[company_id]:
            return "INVALID_REQUESTED_CREDITS"
        if self._host(self_report_url) != self._host(self.company_facility_url[company_id]):
            return "SELF_REPORT_DOMAIN_MISMATCH"
        if not self._is_trusted_host(self._host(satellite_url)):
            return "UNTRUSTED_SATELLITE_SOURCE"
        if not self._is_trusted_host(self._host(sensor_url)):
            return "UNTRUSTED_SENSOR_SOURCE"
        i = u256(0)
        while i < self.report_count:
            if self.report_company_id[i] == company_id and self.report_period[i] == period:
                return "PERIOD_ALREADY_SUBMITTED"
            i = i + u256(1)

        report_id = self.report_count
        self.report_company_id[report_id] = company_id
        self.report_period[report_id] = period
        self.report_self_url[report_id] = self_report_url
        self.report_satellite_url[report_id] = satellite_url
        self.report_sensor_url[report_id] = sensor_url
        self.report_challenge_url[report_id] = ""
        self.report_requested_credits[report_id] = requested_credits
        self.report_status[report_id] = "PENDING_AUDIT"
        self.report_decision[report_id] = "UNDECIDED"
        self.report_proposed_credits[report_id] = u256(0)
        self.report_awarded_credits[report_id] = u256(0)
        self.report_alignment_score[report_id] = u256(0)
        self.report_greenwash_risk[report_id] = u256(0)
        self.report_ecology_score[report_id] = u256(0)
        self.report_verified_reduction[report_id] = u256(0)
        self.report_ai_reason[report_id] = "Awaiting GenLayer audit."
        self.report_finalized[report_id] = u256(0)
        self.report_count = report_id + u256(1)
        return str(report_id)

    @gl.public.write
    def audit_report(self, report_id: u256) -> typing.Any:
        if report_id >= self.report_count:
            return "INVALID_REPORT_ID"
        if self.report_status[report_id] != "PENDING_AUDIT":
            return "REPORT_NOT_PENDING"
        company_id = self.report_company_id[report_id]
        facility_url = self.company_facility_url[company_id]
        self_url = self.report_self_url[report_id]
        satellite_url = self.report_satellite_url[report_id]
        sensor_url = self.report_sensor_url[report_id]

        def run_audit() -> str:
            try:
                facility = str(gl.nondet.web.render(facility_url, mode="html"))[:1800]
                self_report = str(gl.nondet.web.render(self_url, mode="html"))[:2600]
                satellite = str(gl.nondet.web.render(satellite_url, mode="html"))[:1800]
                sensor = str(gl.nondet.web.render(sensor_url, mode="html"))[:1800]
            except Exception:
                return json.dumps({"evidence_alignment_score": 0, "ecology_score": 0, "greenwash_risk": 100, "verified_reduction_tons": 0, "reason": "One or more evidence sources were unreadable."}, sort_keys=True, separators=(",", ":"))
            prompt = f"""You are the GreenTrace carbon audit jury.
Compare the company claim with independent satellite and sensor evidence.
FACILITY: {facility}
COMPANY REPORT: {self_report}
SATELLITE SOURCE: {satellite}
SENSOR SOURCE: {sensor}
Return ONLY JSON with evidence_alignment_score 0-100, ecology_score 0-100,
greenwash_risk 0-100, verified_reduction_tons as a non-negative integer,
and one concise source-grounded reason. Do not choose the final credit amount."""
            return gl.nondet.exec_prompt(prompt)

        principle = "The deterministic decision band produced by alignment, ecology, and greenwash risk must match. Verified reduction must be in the same conservative band. Reasons may differ but must rely on compatible source evidence."
        parsed = self._parse_audit(gl.eq_principle.prompt_comparative(run_audit, principle))
        if parsed is None:
            return "INVALID_AI_RESPONSE"
        alignment, ecology, risk, reduction, reason = parsed
        baseline = self.company_baseline_tons[company_id]
        if reduction > baseline:
            reduction = baseline
        decision = self._decision_for(alignment, ecology, risk)
        credits = self._credits_for(decision, self.report_requested_credits[report_id])
        self.report_alignment_score[report_id] = alignment
        self.report_ecology_score[report_id] = ecology
        self.report_greenwash_risk[report_id] = risk
        self.report_verified_reduction[report_id] = reduction
        self.report_decision[report_id] = decision
        self.report_proposed_credits[report_id] = credits
        self.report_ai_reason[report_id] = reason
        self.report_status[report_id] = "NEEDS_REVIEW" if decision == "NEEDS_REVIEW" else "AUDIT_PROPOSED"
        return self.get_report(report_id)

    @gl.public.write
    def challenge_report(self, report_id: u256, challenge_url: str) -> typing.Any:
        if report_id >= self.report_count:
            return "INVALID_REPORT_ID"
        if self.report_status[report_id] != "AUDIT_PROPOSED":
            return "AUDIT_NOT_CHALLENGEABLE"
        company_id = self.report_company_id[report_id]
        sender = gl.message.sender_address
        if sender != self.company_owner[company_id] and sender != self.source_admin:
            return "NOT_AUTHORIZED_CHALLENGER"
        if not self._is_trusted_host(self._host(challenge_url)):
            return "UNTRUSTED_CHALLENGE_SOURCE"
        self.report_challenge_url[report_id] = challenge_url
        self.report_challenger[report_id] = sender
        self.report_status[report_id] = "CHALLENGE_PENDING"
        return "CHALLENGE_OPENED"

    @gl.public.write
    def audit_challenge(self, report_id: u256) -> typing.Any:
        if report_id >= self.report_count:
            return "INVALID_REPORT_ID"
        if self.report_status[report_id] != "CHALLENGE_PENDING":
            return "CHALLENGE_NOT_PENDING"
        original_reason = self.report_ai_reason[report_id]
        challenge_url = self.report_challenge_url[report_id]

        def run_challenge() -> str:
            try:
                challenge = str(gl.nondet.web.render(challenge_url, mode="html"))[:3000]
            except Exception:
                return json.dumps({"evidence_alignment_score": 0, "ecology_score": 0, "greenwash_risk": 100, "verified_reduction_tons": 0, "reason": "Challenge evidence was unreadable."}, sort_keys=True, separators=(",", ":"))
            prompt = f"""Reconsider a GreenTrace audit using trusted challenge evidence.
ORIGINAL AUDIT: {original_reason}
CHALLENGE EVIDENCE: {challenge}
Return ONLY JSON with evidence_alignment_score, ecology_score, greenwash_risk,
verified_reduction_tons, and one concise reason. Do not choose the credit amount."""
            return gl.nondet.exec_prompt(prompt)

        principle = "The deterministic decision band must match, verified reduction must be in the same conservative band, and the challenge must be treated consistently. Reason wording may differ."
        parsed = self._parse_audit(gl.eq_principle.prompt_comparative(run_challenge, principle))
        if parsed is None:
            return "INVALID_AI_RESPONSE"
        alignment, ecology, risk, reduction, reason = parsed
        company_id = self.report_company_id[report_id]
        if reduction > self.company_baseline_tons[company_id]:
            reduction = self.company_baseline_tons[company_id]
        decision = self._decision_for(alignment, ecology, risk)
        self.report_alignment_score[report_id] = alignment
        self.report_ecology_score[report_id] = ecology
        self.report_greenwash_risk[report_id] = risk
        self.report_verified_reduction[report_id] = reduction
        self.report_decision[report_id] = decision
        self.report_proposed_credits[report_id] = self._credits_for(decision, self.report_requested_credits[report_id])
        self.report_ai_reason[report_id] = reason
        self.report_status[report_id] = "CHALLENGE_RULING"
        return self.get_report(report_id)

    @gl.public.write
    def finalize_issuance(self, report_id: u256) -> typing.Any:
        if report_id >= self.report_count:
            return "INVALID_REPORT_ID"
        if gl.message.sender_address != self.source_admin:
            return "NOT_SOURCE_ADMIN"
        status = self.report_status[report_id]
        if status != "AUDIT_PROPOSED" and status != "CHALLENGE_RULING":
            return "AUDIT_NOT_FINALIZABLE"
        if self.report_finalized[report_id] != u256(0):
            return "ALREADY_FINALIZED"
        company_id = self.report_company_id[report_id]
        owner = self.company_owner[company_id]
        awarded = self.report_proposed_credits[report_id]
        reduction = self.report_verified_reduction[report_id]
        self.report_finalized[report_id] = u256(1)
        self.report_awarded_credits[report_id] = awarded
        self.report_status[report_id] = "FINALIZED"
        if awarded > u256(0):
            self.wallet_credit_balance[owner] = self.wallet_credit_balance[owner] + awarded
            self.company_total_verified_reduction[company_id] = self.company_total_verified_reduction[company_id] + reduction
            self.total_credits_issued = self.total_credits_issued + awarded
        return self.get_report(report_id)

    @gl.public.write
    def transfer_credits(self, to_wallet: str, amount: u256) -> typing.Any:
        sender = gl.message.sender_address
        recipient = Address(to_wallet)
        if amount == u256(0):
            return "INVALID_AMOUNT"
        balance = self.wallet_credit_balance[sender]
        if amount > balance:
            return "INSUFFICIENT_CREDITS"
        self.wallet_credit_balance[sender] = balance - amount
        self.wallet_credit_balance[recipient] = self.wallet_credit_balance[recipient] + amount
        transfer_id = self.transfer_count
        self.transfer_from_wallet[transfer_id] = sender
        self.transfer_to_wallet[transfer_id] = recipient
        self.transfer_amount[transfer_id] = amount
        self.transfer_count = transfer_id + u256(1)
        return str(transfer_id)

    @gl.public.write
    def retire_credits(self, amount: u256, beneficiary: str, reference: str) -> typing.Any:
        owner = gl.message.sender_address
        if amount == u256(0):
            return "INVALID_AMOUNT"
        if len(beneficiary) == 0 or len(reference) == 0:
            return "INVALID_RETIREMENT_DETAILS"
        balance = self.wallet_credit_balance[owner]
        if amount > balance:
            return "INSUFFICIENT_CREDITS"
        self.wallet_credit_balance[owner] = balance - amount
        retirement_id = self.retirement_count
        self.retirement_owner[retirement_id] = owner
        self.retirement_amount[retirement_id] = amount
        self.retirement_beneficiary[retirement_id] = beneficiary[:200]
        self.retirement_reference[retirement_id] = reference[:300]
        self.retirement_count = retirement_id + u256(1)
        self.total_credits_retired = self.total_credits_retired + amount
        return str(retirement_id)

    @gl.public.view
    def get_company_count(self) -> u256:
        return self.company_count

    @gl.public.view
    def get_report_count(self) -> u256:
        return self.report_count

    @gl.public.view
    def get_trusted_source_count(self) -> u256:
        return u256(len(self.trusted_source_hosts))

    @gl.public.view
    def get_trusted_source(self, source_id: u256) -> str:
        if source_id >= u256(len(self.trusted_source_hosts)):
            return "INVALID_SOURCE_ID"
        return self.trusted_source_hosts[source_id]

    @gl.public.view
    def get_wallet_balance(self, wallet: str) -> u256:
        return self.wallet_credit_balance[Address(wallet)]

    @gl.public.view
    def get_market_stats(self) -> str:
        return json.dumps({"company_count": str(self.company_count), "report_count": str(self.report_count), "retirement_count": str(self.retirement_count), "source_count": str(len(self.trusted_source_hosts)), "total_credits_issued": str(self.total_credits_issued), "total_credits_retired": str(self.total_credits_retired), "transfer_count": str(self.transfer_count)}, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_company(self, company_id: u256) -> str:
        if company_id >= self.company_count:
            return json.dumps({"error": "INVALID_COMPANY_ID"}, sort_keys=True, separators=(",", ":"))
        owner = self.company_owner[company_id]
        return json.dumps({"baseline_tons": str(self.company_baseline_tons[company_id]), "credit_balance": str(self.wallet_credit_balance[owner]), "facility_url": self.company_facility_url[company_id], "industry": self.company_industry[company_id], "name": self.company_name[company_id], "owner": owner.as_hex, "status": self.company_status[company_id], "total_verified_reduction": str(self.company_total_verified_reduction[company_id])}, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_report(self, report_id: u256) -> str:
        if report_id >= self.report_count:
            return json.dumps({"error": "INVALID_REPORT_ID"}, sort_keys=True, separators=(",", ":"))
        return json.dumps({"alignment_score": str(self.report_alignment_score[report_id]), "awarded_credits": str(self.report_awarded_credits[report_id]), "challenge_url": self.report_challenge_url[report_id], "company_id": str(self.report_company_id[report_id]), "decision": self.report_decision[report_id], "ecology_score": str(self.report_ecology_score[report_id]), "finalized": str(self.report_finalized[report_id]), "greenwash_risk": str(self.report_greenwash_risk[report_id]), "period": self.report_period[report_id], "proposed_credits": str(self.report_proposed_credits[report_id]), "reason": self.report_ai_reason[report_id], "requested_credits": str(self.report_requested_credits[report_id]), "satellite_url": self.report_satellite_url[report_id], "self_report_url": self.report_self_url[report_id], "sensor_url": self.report_sensor_url[report_id], "status": self.report_status[report_id], "verified_reduction": str(self.report_verified_reduction[report_id])}, sort_keys=True, separators=(",", ":"))
