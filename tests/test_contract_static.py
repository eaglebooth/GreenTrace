import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "GreenTrace.py"


class GreenTraceV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = CONTRACT.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def section(self, start: str, end: str) -> str:
        return self.source[self.source.index(start):self.source.index(end)]

    def test_runtime_header(self):
        lines = self.source.splitlines()
        self.assertEqual(lines[0], "# v0.2.16")
        self.assertEqual(lines[1], '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }')

    def test_owner_is_derived_and_address_typed(self):
        self.assertIn("company_owner: TreeMap[u256, Address]", self.source)
        register = self.section("def register_company", "def submit_report")
        self.assertIn("owner = gl.message.sender_address", register)
        self.assertNotIn("wallet:", register)

    def test_company_writes_are_authorized(self):
        submit = self.section("def submit_report", "def audit_report")
        self.assertIn('return "NOT_COMPANY_OWNER"', submit)
        transfer = self.section("def transfer_credits", "def retire_credits")
        self.assertIn("sender = gl.message.sender_address", transfer)

    def test_subjective_audits_use_comparative_consensus(self):
        self.assertNotIn("gl.eq_principle.strict_eq", self.source)
        self.assertEqual(self.source.count("gl.eq_principle.prompt_comparative"), 2)

    def test_current_web_render_api(self):
        self.assertIn('mode="html"', self.source)
        self.assertNotIn("media_type=", self.source)
        self.assertNotIn(".body.decode", self.source)

    def test_sources_are_constrained(self):
        self.assertIn("trusted_source_hosts: DynArray[str]", self.source)
        self.assertIn('return "UNTRUSTED_SATELLITE_SOURCE"', self.source)
        self.assertIn('return "UNTRUSTED_SENSOR_SOURCE"', self.source)
        self.assertIn('return "SELF_REPORT_DOMAIN_MISMATCH"', self.source)

    def test_duplicate_period_and_bounds_guards(self):
        self.assertIn('return "PERIOD_ALREADY_SUBMITTED"', self.source)
        self.assertIn("requested_credits > self.company_baseline_tons", self.source)
        self.assertIn("if reduction > baseline", self.source)

    def test_deterministic_thresholds_and_finalization(self):
        self.assertIn("def _decision_for", self.source)
        self.assertIn("def _credits_for", self.source)
        finalize = self.section("def finalize_issuance", "def transfer_credits")
        self.assertIn('return "NOT_SOURCE_ADMIN"', finalize)
        self.assertIn('return "ALREADY_FINALIZED"', finalize)

    def test_credit_ownership_and_retirement(self):
        self.assertIn("wallet_credit_balance: TreeMap[Address, u256]", self.source)
        self.assertIn("def transfer_credits", self.source)
        self.assertIn("def retire_credits", self.source)
        self.assertIn("total_credits_retired", self.source)


if __name__ == "__main__":
    unittest.main()
