"""
Layer 1 — Navigation Walkthrough Generator

Transforms parsed Tosca test steps into step-by-step navigation walkthroughs
that tell a user "I'm not lost" — how to get through a transaction screen by screen.

Input:  Parsed ToscaTestScript(s) + Opal overlay
Output: Markdown walkthrough document per transaction
"""

from pathlib import Path
from .base import BaseGenerator


class WalkthroughGenerator(BaseGenerator):
    """Generates navigation walkthroughs from Tosca test scripts."""

    PROMPT_TEMPLATE = "walkthrough.txt"
    OUTPUT_SUBDIR = "walkthroughs"
    OUTPUT_EXT = ".md"

    def generate(self, parsed_data: dict, overlay_data: dict) -> list[Path]:
        """
        Generate a walkthrough for each Tosca test script.

        Args:
            parsed_data: Dict with 'tosca_scripts' key → list of ToscaTestScript
            overlay_data: Resolved overlay data

        Returns:
            List of paths to generated walkthrough files
        """
        scripts = parsed_data.get("tosca_scripts", [])
        if not scripts:
            print("  ⚠️  No Tosca scripts provided, skipping walkthrough generation")
            return []

        template = self.load_template()
        scope = self._get_scope_vars()
        outputs = []

        for script in scripts:
            print(f"  Generating walkthrough for: {script.name}")

            # Build template variables
            variables = {
                **scope,
                "script_name": script.name,
                "transaction_code": script.transaction or self._extract_transaction(script),
                "steps_data": self._format_steps_for_prompt(script.user_action_steps),
                "test_data": self._format_test_data_for_prompt(script.test_data),
                "site_constraints": self._format_site_constraints_for_transaction(
                    overlay_data, script.transaction or self._extract_transaction(script)
                ),
            }

            # Render and call Claude
            prompt = self.render_prompt(template, variables)
            content = self.call_claude(prompt, max_tokens=4096)

            # Write output
            safe_name = script.name.lower().replace(" ", "_").replace("/", "_")
            filename = f"walkthrough_{safe_name}{self.OUTPUT_EXT}"
            path = self.write_output(content, filename)
            outputs.append(path)
            print(f"  ✅ Written: {path}")

        return outputs

    def _extract_transaction(self, script) -> str:
        """Try to extract transaction code from script metadata or steps."""
        # Check if any step navigates to a transaction
        for step in script.steps:
            if step.target_url and step.action_type == "NAVIGATE":
                url = step.target_url
                # SAP transaction codes are typically in the URL or description
                if "/sap/" in url.lower():
                    parts = url.split("/")
                    for part in parts:
                        if part.isupper() and 2 <= len(part) <= 10:
                            return part
        return ""

    def _format_site_constraints_for_transaction(
        self, overlay_data: dict, transaction_code: str
    ) -> str:
        """Get site constraints specific to a transaction."""
        if not overlay_data or "overlays" not in overlay_data:
            return "(no site-specific constraints for this transaction)"

        lines = []
        for overlay in overlay_data.get("overlays", []):
            # Match by transaction code
            if overlay.get("transaction", "") == transaction_code:
                for variation in overlay.get("variations", []):
                    v_type = variation.get("type", "")
                    label = variation.get("field", variation.get("step", ""))
                    enterprise = variation.get("enterprise_default", "")
                    site = variation.get("site_override", "")
                    reason = variation.get("reason", "")
                    lines.append(f"⚠️ {label} [{v_type}]")
                    lines.append(f"  Enterprise default: {enterprise}")
                    lines.append(f"  {self.scope.get('site_code', 'Site')} override: {site}")
                    lines.append(f"  Reason: {reason}")
                    lines.append("")

        return "\n".join(lines) if lines else "(no site-specific constraints for this transaction)"
