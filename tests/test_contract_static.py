import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "GreenTrace.py"


class GreenTraceContractStaticTests(unittest.TestCase):
    def setUp(self):
        self.source = CONTRACT.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)

    def test_header_and_imports(self):
        lines = self.source.splitlines()
        self.assertEqual(lines[0], "# v0.2.16")
        self.assertEqual(
            lines[1],
            '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }',
        )
        self.assertEqual(lines[2], "from genlayer import *")

        imports = [
            node
            for node in self.tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        rendered = []
        for node in imports:
            if isinstance(node, ast.ImportFrom):
                rendered.append(f"from {node.module} import *")
            else:
                rendered.extend(f"import {alias.name}" for alias in node.names)
        self.assertEqual(rendered, ["from genlayer import *", "import typing", "import json"])

    def test_storage_allowed_types(self):
        contract = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.ClassDef) and node.name == "GreenTrace"
        )
        allowed_scalars = {"u256"}
        for node in contract.body:
            if not isinstance(node, ast.AnnAssign):
                continue
            annotation = ast.unparse(node.annotation)
            is_allowed_map = annotation in {"TreeMap[u256, str]", "TreeMap[u256, u256]"}
            is_allowed_array = annotation in {"DynArray[str]", "DynArray[u256]"}
            is_allowed_scalar = annotation in allowed_scalars
            self.assertTrue(
                is_allowed_map or is_allowed_array or is_allowed_scalar,
                f"Forbidden storage annotation: {annotation}",
            )

    def test_public_signatures(self):
        contract = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.ClassDef) and node.name == "GreenTrace"
        )
        allowed = {"u256", "str", "typing.Any"}
        for node in contract.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            decorators = [ast.unparse(decorator) for decorator in node.decorator_list]
            if not any(decorator in {"gl.public.write", "gl.public.view"} for decorator in decorators):
                continue
            params = [arg for arg in node.args.args if arg.arg != "self"]
            self.assertLessEqual(len(params), 6, f"{node.name} has too many params")
            for param in params:
                self.assertIsNotNone(param.annotation, f"{node.name}.{param.arg} is untyped")
                rendered = ast.unparse(param.annotation)
                self.assertIn(rendered, allowed, f"{node.name}.{param.arg}: {rendered}")
            self.assertIsNotNone(node.returns, f"{node.name} is missing return type")
            self.assertIn(ast.unparse(node.returns), allowed, f"{node.name} return type")

    def test_nondet_wrapped_in_consensus(self):
        self.assertIn("gl.nondet.web.render", self.source)
        self.assertIn("gl.nondet.exec_prompt", self.source)
        self.assertIn("gl.eq_principle.strict_eq", self.source)

    def test_carbon_credit_domain_logic_present(self):
        self.assertIn("greenwash_risk", self.source)
        self.assertIn("credits_awarded", self.source)
        self.assertIn("transfer_credits", self.source)


if __name__ == "__main__":
    unittest.main()
