"""
process_rationale.py — Layer 5: Process Rationale & Consequence Generator

Generates a "When and Why" guide for a given process: decision maps,
anti-patterns with consequence tables, and compliance context.

Source assets used:
  - poc/data/consequences.yaml   (anti-patterns, consequences, compliance)
  - poc/data/bpmn/*.xml          (decision gateways, process variants)
  - poc/data/tosca/*.xml         (test cases, including negative/validation)
  - poc/data/opal_overlay.yaml   (site-specific rules)

Output: Markdown document, one per process in consequences.yaml

SME review required before publication. Consequence descriptions and
compliance references must be verified against actual system configuration.
"""

import os
import yaml
from pathlib import Path
from generators.base import BaseGenerator

# Optional imports for parsers — graceful fallback if not available
try:
    from parsers.bpmn_parser import BPMNParser
    from parsers.tosca_parser import ToscaParser
    _PARSERS_AVAILABLE = True
except ImportError:
    _PARSERS_AVAILABLE = False


class ProcessRationaleGenerator(BaseGenerator):
    """
    Layer 5 generator. Produces one 'When and Why' guide per process
    defined in consequences.yaml.
    """

    def __init__(self, config: dict, overlay_assembler=None):
        super().__init__(config)
        self.overlay = overlay_assembler
        self._consequences = None

    # ── Data loading ──────────────────────────────────────────────────────────

    def load_consequences(self) -> list:
        """Load and cache consequences.yaml."""
        if self._consequences is not None:
            return self._consequences

        data_dir = Path(self.config.get("data_dir", "poc/data"))
        consequences_path = data_dir / "consequences.yaml"

        if not consequences_path.exists():
            raise FileNotFoundError(
                f"consequences.yaml not found at {consequences_path}. "
                "This file is required for Layer 5 generation. "
                "See docs/layers/layer-5-process-rationale.md for the schema."
            )

        with open(consequences_path) as f:
            data = yaml.safe_load(f)

        self._consequences = data.get("processes", [])
        return self._consequences

    def _format_anti_patterns(self, process: dict) -> str:
        """Format anti-patterns for inclusion in the prompt."""
        anti_patterns = process.get("anti_patterns", [])
        if not anti_patterns:
            return "No anti-patterns documented for this process yet."

        lines = []
        for ap in anti_patterns:
            lines.append(f"ANTI-PATTERN: {ap.get('name', 'Unnamed')}")
            lines.append(f"  Why it feels right: {ap.get('why_feels_right', '').strip()}")
            lines.append(f"  Why it is wrong: {ap.get('why_wrong', '').strip()}")
            lines.append(f"  Immediate consequence: {ap.get('immediate_consequence', '')}")
            lines.append("  Downstream consequences:")
            for c in ap.get("consequences", []):
                sev = c.get("severity", "medium").upper()
                lines.append(f"    [{sev}] {c.get('category', '').upper()}: {c.get('description', '').strip()}")
            recovery = ap.get("recovery", "").strip()
            if recovery:
                lines.append(f"  Recovery: {recovery}")
            lines.append("")

        return "\n".join(lines)

    def _format_compliance(self, process: dict) -> str:
        """Format compliance context for the prompt."""
        c = process.get("compliance", {})
        if not c:
            return "No compliance context documented for this process."

        return (
            f"Regulation: {c.get('regulation', '')}\n"
            f"Control name: {c.get('control_name', '')}\n"
            f"Control objective: {c.get('control_objective', '').strip()}\n"
            f"Audit question: {c.get('audit_question', '').strip()}\n"
            f"Audit risk: {c.get('audit_risk', '').strip()}\n"
            f"SE-DC specific: {c.get('se_dc_threshold', '').strip()}"
        )

    def _format_decision_map(self, process: dict) -> str:
        """Format the decision map (process variants) for the prompt."""
        dm = process.get("decision_map", [])
        if not dm:
            return "No decision map defined — derive from BPMN gateway conditions."

        lines = []
        for row in dm:
            lines.append(f"Scenario: {row.get('scenario', '')}")
            lines.append(f"  Correct process: {row.get('correct_process', '')}")
            if row.get("movement_type"):
                lines.append(f"  Movement type: {row['movement_type']}")
            if row.get("notes"):
                lines.append(f"  Notes: {row['notes'].strip()}")
            lines.append("")
        return "\n".join(lines)

    def _format_bpmn_decisions(self, process: dict) -> str:
        """Extract decision gateway conditions from the BPMN file."""
        if not _PARSERS_AVAILABLE:
            return "BPMN parser not available — using consequences.yaml decision map only."

        bpmn_ref = process.get("bpmn_ref")
        if not bpmn_ref:
            return "No BPMN reference — using consequences.yaml decision map only."

        data_dir = Path(self.config.get("data_dir", "poc/data"))
        bpmn_path = data_dir / "bpmn" / bpmn_ref
        if not bpmn_path.exists():
            return f"BPMN file not found: {bpmn_path}"

        try:
            parser = BPMNParser()
            model = parser.parse(str(bpmn_path))
            lines = []
            for element in model.elements:
                if hasattr(element, "conditions"):  # Gateway
                    lines.append(f"Gateway: {element.name}")
                    for cond in element.conditions:
                        lines.append(f"  → {cond}")
            return "\n".join(lines) if lines else "No gateways found in BPMN model."
        except Exception as e:
            return f"Could not parse BPMN: {e}"

    def _format_tosca_test_cases(self, process: dict) -> str:
        """Extract relevant test cases (including negative cases) from Tosca."""
        if not _PARSERS_AVAILABLE:
            return "Tosca parser not available."

        tosca_ref = process.get("tosca_ref")
        if not tosca_ref:
            return "No Tosca reference for this process."

        data_dir = Path(self.config.get("data_dir", "poc/data"))
        tosca_path = data_dir / "tosca" / tosca_ref
        if not tosca_path.exists():
            return f"Tosca file not found: {tosca_path}"

        try:
            parser = ToscaParser()
            scripts = parser.parse(str(tosca_path))
            lines = []
            for script in scripts[:3]:  # limit to first 3 test cases for prompt size
                lines.append(f"Test case: {script.name}")
                for step in script.steps[:6]:  # first 6 steps per case
                    lines.append(f"  {step.action}: {step.target} = {step.value}")
            return "\n".join(lines) if lines else "No test cases found."
        except Exception as e:
            return f"Could not parse Tosca: {e}"

    def _get_site_constraints(self, transaction_code: str) -> str:
        """Pull site-specific rules for this transaction from Opal overlay."""
        if not self.overlay:
            return "Opal overlay not loaded."
        try:
            resolved = self.overlay.resolve("BUYER")  # default to BUYER role for rationale
            constraints = resolved.get("variations", [])
            relevant = [
                c for c in constraints
                if transaction_code and transaction_code in str(c.get("transaction", ""))
            ]
            if not relevant:
                return "No site-specific overrides for this transaction in SE-DC overlay."
            return "\n".join(
                f"- {c.get('field', '')}: {c.get('rule', '')} [{c.get('reason', '')}]"
                for c in relevant
            )
        except Exception as e:
            return f"Could not read overlay: {e}"

    # ── Generation ────────────────────────────────────────────────────────────

    def generate_for_process(self, process: dict, output_dir: Path) -> dict:
        """
        Generate one Process Rationale guide for the given process entry.
        Returns a result dict compatible with the main pipeline summary.
        """
        process_id = process.get("id", "unknown")
        process_name = process.get("name", process_id)
        transaction = process.get("transaction", "")

        output_path = output_dir / f"process_rationale_{process_id}.md"

        site_info = {}
        if self.overlay:
            try:
                resolved = self.overlay.resolve("BUYER")
                site_info = resolved.get("site", {})
            except Exception:
                pass

        prompt_vars = {
            "company":           site_info.get("company", "GlobalMart"),
            "site":              site_info.get("name", "SE-DC"),
            "system":            site_info.get("system", "SAP S/4HANA 2023"),
            "process_name":      process_name,
            "transaction_code":  transaction,
            "role":              "Operations / Receiving Team",
            "process_area":      process.get("process_area", ""),
            "process_description": process.get("description", "").strip(),
            "decision_points":   self._format_bpmn_decisions(process),
            "test_cases":        self._format_tosca_test_cases(process),
            "site_constraints":  self._get_site_constraints(transaction),
            "anti_patterns_data": self._format_anti_patterns(process),
            "compliance_data":   self._format_compliance(process),
        }

        prompt = self.render_prompt("process_rationale", prompt_vars)
        content = self.call_claude(prompt, max_tokens=2500)

        # Add SME review header
        header = (
            f"<!-- SME REVIEW REQUIRED — DO NOT PUBLISH WITHOUT APPROVAL -->\n"
            f"<!-- Layer 5: Process Rationale & Consequence -->\n"
            f"<!-- Process: {process_name} | Site: {site_info.get('name', 'SE-DC')} -->\n"
            f"<!-- Generated: run pipeline to update timestamp -->\n\n"
        )
        output_path.write_text(header + content, encoding="utf-8")

        return {
            "layer": 5,
            "type": "process_rationale",
            "process": process_name,
            "transaction": transaction,
            "output": str(output_path),
            "status": "generated — SME review required",
        }

    def generate_all(self, output_dir: Path) -> list:
        """
        Generate Process Rationale guides for all processes in consequences.yaml.
        Returns list of result dicts.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        processes = self.load_consequences()

        if not processes:
            return [{
                "layer": 5,
                "type": "process_rationale",
                "status": "skipped — no processes defined in consequences.yaml",
            }]

        results = []
        for process in processes:
            print(f"  Layer 5 → {process.get('name', process.get('id'))}")
            result = self.generate_for_process(process, output_dir)
            results.append(result)

        return results
