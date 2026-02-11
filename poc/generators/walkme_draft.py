"""
Layer 4 — WalkMe Flow Draft Generator

Transforms parsed Tosca test steps with UI element identifiers into WalkMe-style
flow definitions that provide in-application guidance: "Help me while I'm doing it."

Input:  Parsed ToscaTestScript(s) + Opal overlay
Output: JSON WalkMe flow definition per transaction
"""

import json
from pathlib import Path
from .base import BaseGenerator


class WalkMeDraftGenerator(BaseGenerator):
    """Generates WalkMe Smart Walk-Thru flow definitions from Tosca scripts."""

    PROMPT_TEMPLATE = "walkme.txt"
    OUTPUT_SUBDIR = "walkme_flows"
    OUTPUT_EXT = ".json"

    def generate(self, parsed_data: dict, overlay_data: dict) -> list[Path]:
        """
        Generate a WalkMe flow for each Tosca test script.

        Args:
            parsed_data: Dict with 'tosca_scripts' key → list of ToscaTestScript
            overlay_data: Resolved overlay data

        Returns:
            List of paths to generated WalkMe JSON files
        """
        scripts = parsed_data.get("tosca_scripts", [])
        if not scripts:
            print("  ⚠️  No Tosca scripts provided, skipping WalkMe generation")
            return []

        template = self.load_template()
        scope = self._get_scope_vars()
        outputs = []

        for script in scripts:
            print(f"  Generating WalkMe flow for: {script.name}")

            transaction = script.transaction or self._extract_transaction(script)

            variables = {
                **scope,
                "script_name": script.name,
                "transaction_code": transaction,
                "steps_with_elements": self._format_steps_with_elements(script),
                "site_constraints": self._format_site_constraints_for_transaction(
                    overlay_data, transaction
                ),
            }

            # Render and call Claude
            prompt = self.render_prompt(template, variables)
            raw_response = self.call_claude(prompt, max_tokens=6000)

            # Parse and validate JSON
            content = self._extract_and_validate_json(raw_response)

            # Write output
            safe_name = script.name.lower().replace(" ", "_").replace("/", "_")
            filename = f"walkme_{safe_name}{self.OUTPUT_EXT}"
            path = self.write_output(content, filename)
            outputs.append(path)
            print(f"  ✅ Written: {path}")

        return outputs

    def _format_steps_with_elements(self, script) -> str:
        """Format steps with UI element details for WalkMe targeting."""
        lines = []
        for step in script.user_action_steps:
            line = f"Step {step.step_number}: [{step.action_type}] {step.description}"
            if step.element:
                line += f"\n  Element ID: {step.element.identifier}"
                if step.element.description:
                    line += f"\n  Element Description: {step.element.description}"
            if step.value:
                line += f"\n  Value: {step.value}"
            if step.target_url:
                line += f"\n  Navigate: {step.target_url}"
            if step.expected_result:
                line += f"\n  Expected Result: {step.expected_result}"

            # Include assertions (they become WalkMe validations)
            if step.assertions:
                for a in step.assertions:
                    parts = [f"  Validation [{a.type}]"]
                    if a.field_reference:
                        parts.append(f"Field: {a.field_reference}")
                    if a.expected_value:
                        parts.append(f"Expected: {a.expected_value}")
                    if a.allowed_values:
                        parts.append(f"Allowed: {a.allowed_values}")
                    if a.reason:
                        parts.append(f"Reason: {a.reason}")
                    line += "\n  " + " | ".join(parts)

            # Check if this step has site-specific annotations
            site_annotations = [
                ann for ann in script.annotations
                if ann.step_id == step.step_id and "SPECIFIC" in ann.type.upper()
            ]
            if site_annotations:
                for ann in site_annotations:
                    line += f"\n  ⚠️ SITE-SPECIFIC: {ann.description}"

            lines.append(line)
        return "\n\n".join(lines)

    def _extract_and_validate_json(self, raw_response: str) -> str:
        """
        Extract JSON from Claude's response, validate it, and return formatted JSON.

        Claude might wrap the JSON in markdown code fences — strip those.
        """
        text = raw_response.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            # Remove first line (```json or ```)
            lines = text.split("\n")
            start = 1
            end = len(lines)
            for i in range(len(lines) - 1, 0, -1):
                if lines[i].strip() == "```":
                    end = i
                    break
            text = "\n".join(lines[start:end])

        # Try to parse
        try:
            data = json.loads(text)
            # Re-serialize with pretty formatting
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            print(f"  ⚠️  Warning: Claude returned invalid JSON, saving raw response")
            print(f"     Error: {e}")
            # Wrap in a comment so it's clear this needs review
            fallback = {
                "_error": "Claude returned invalid JSON — manual review needed",
                "_raw_response": text[:2000],  # Truncate if very long
            }
            return json.dumps(fallback, indent=2)

    def _extract_transaction(self, script) -> str:
        """Try to extract transaction code from script."""
        for step in script.steps:
            if step.target_url and step.action_type == "NAVIGATE":
                url = step.target_url
                if "/sap/" in url.lower():
                    parts = url.split("/")
                    for part in parts:
                        if part.isupper() and 2 <= len(part) <= 10:
                            return part
        return ""

    def _format_site_constraints_for_transaction(
        self, overlay_data: dict, transaction_code: str
    ) -> str:
        """Get site constraints for a specific transaction."""
        if not overlay_data or "overlays" not in overlay_data:
            return "(no site-specific constraints)"

        lines = []
        for overlay in overlay_data.get("overlays", []):
            if overlay.get("transaction", "") == transaction_code:
                for variation in overlay.get("variations", []):
                    v_type = variation.get("type", "")
                    label = variation.get("field", variation.get("step", ""))
                    enterprise = variation.get("enterprise_default", "")
                    site = variation.get("site_override", "")
                    reason = variation.get("reason", "")
                    lines.append(f"⚠️ {label} [{v_type}]")
                    lines.append(f"  Enterprise: {enterprise}")
                    lines.append(f"  {self.scope.get('site_code', 'Site')}: {site}")
                    lines.append(f"  Reason: {reason}")
                    lines.append("")

        return "\n".join(lines) if lines else "(no site-specific constraints)"
