"""
Layer 3 — Role-Specific Job Aid Generator

Transforms parsed Tosca test steps + BPMN process context into concise,
printable job aids that tell a user "I can do my job" — quick desk reference
with key fields, steps, and site-specific rules.

Input:  Parsed ToscaTestScript(s) + BpmnProcess + Opal overlay
Output: Markdown job aid (later converted to docx by assembler)
"""

from pathlib import Path
from .base import BaseGenerator


class JobAidGenerator(BaseGenerator):
    """Generates role-specific job aids from Tosca scripts and BPMN context."""

    PROMPT_TEMPLATE = "job_aid.txt"
    OUTPUT_SUBDIR = "job_aids"
    OUTPUT_EXT = ".md"

    def generate(self, parsed_data: dict, overlay_data: dict) -> list[Path]:
        """
        Generate a job aid for each Tosca test script, enriched with BPMN context.

        Args:
            parsed_data: Dict with 'tosca_scripts' and 'bpmn_processes' keys
            overlay_data: Resolved overlay data

        Returns:
            List of paths to generated job aid files
        """
        scripts = parsed_data.get("tosca_scripts", [])
        processes = parsed_data.get("bpmn_processes", [])

        if not scripts:
            print("  ⚠️  No Tosca scripts provided, skipping job aid generation")
            return []

        template = self.load_template()
        scope = self._get_scope_vars()
        outputs = []

        # Build process context summary from BPMN
        process_context = self._build_process_context(processes)

        for script in scripts:
            print(f"  Generating job aid for: {script.name}")

            transaction = script.transaction or self._extract_transaction(script)

            variables = {
                **scope,
                "script_name": script.name,
                "transaction_code": transaction,
                "steps_data": self._format_steps_for_prompt(script.steps),
                "test_data": self._format_test_data_for_prompt(script.test_data),
                "site_constraints": self._format_site_constraints_for_transaction(
                    overlay_data, transaction
                ),
                "process_context": process_context,
            }

            # Render and call Claude
            prompt = self.render_prompt(template, variables)
            content = self.call_claude(prompt, max_tokens=4096)

            # Write output
            safe_name = script.name.lower().replace(" ", "_").replace("/", "_")
            filename = f"job_aid_{safe_name}{self.OUTPUT_EXT}"
            path = self.write_output(content, filename)
            outputs.append(path)
            print(f"  ✅ Written: {path}")

        return outputs

    def _build_process_context(self, processes) -> str:
        """Build a concise process context summary from BPMN models."""
        if not processes:
            return "(no BPMN process context available)"

        lines = []
        for process in processes:
            lines.append(f"Process: {process.name}")
            if process.roles:
                lines.append(f"  Roles: {', '.join(process.roles)}")
            if process.documentation:
                # Just first 200 chars of documentation
                doc = process.documentation[:200]
                if len(process.documentation) > 200:
                    doc += "..."
                lines.append(f"  Overview: {doc}")

            # List tasks with transaction codes
            tasks_with_tcodes = [
                t for t in process.tasks if t.transaction_code
            ]
            if tasks_with_tcodes:
                lines.append("  Related transactions:")
                for t in tasks_with_tcodes:
                    lines.append(f"    - {t.name} [{t.transaction_code}]")

            # List decision points
            if process.decision_points:
                lines.append("  Key decisions:")
                for gw in process.decision_points:
                    lines.append(f"    - {gw.name}: {gw.documentation[:100]}" if gw.documentation else f"    - {gw.name}")

        return "\n".join(lines)

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
