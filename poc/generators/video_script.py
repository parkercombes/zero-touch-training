"""
Layer 2 — Process Explainer Video Script Generator

Transforms parsed BPMN process models into video scripts that tell a user
"I know where I fit" — understanding the end-to-end process, roles, and handoffs.

Input:  Parsed BpmnProcess + Opal overlay
Output: Markdown video script document
"""

from pathlib import Path
from ..parsers.bpmn_parser import Task, Gateway, Event
from .base import BaseGenerator


class VideoScriptGenerator(BaseGenerator):
    """Generates process explainer video scripts from BPMN process models."""

    PROMPT_TEMPLATE = "video_script.txt"
    OUTPUT_SUBDIR = "video_scripts"
    OUTPUT_EXT = ".md"

    def generate(self, parsed_data: dict, overlay_data: dict) -> list[Path]:
        """
        Generate a video script for each BPMN process model.

        Args:
            parsed_data: Dict with 'bpmn_processes' key → list of BpmnProcess
            overlay_data: Resolved overlay data

        Returns:
            List of paths to generated video script files
        """
        processes = parsed_data.get("bpmn_processes", [])
        if not processes:
            print("  ⚠️  No BPMN processes provided, skipping video script generation")
            return []

        template = self.load_template()
        scope = self._get_scope_vars()
        outputs = []

        for process in processes:
            print(f"  Generating video script for: {process.name}")

            # Build template variables
            variables = {
                **scope,
                "roles": ", ".join(process.roles) if process.roles else "Not specified",
                "process_flow": self._format_process_flow(process),
                "decision_points": self._format_decision_points(process),
                "site_constraints": self._format_site_constraints(overlay_data),
            }

            # Render and call Claude
            prompt = self.render_prompt(template, variables)
            content = self.call_claude(prompt, max_tokens=6000)

            # Write output
            safe_name = process.name.lower().replace(" ", "_").replace("/", "_")
            filename = f"video_script_{safe_name}{self.OUTPUT_EXT}"
            path = self.write_output(content, filename)
            outputs.append(path)
            print(f"  ✅ Written: {path}")

        return outputs

    def _format_process_flow(self, process) -> str:
        """Format the ordered process flow for the prompt."""
        lines = []
        for i, element in enumerate(process.ordered_elements, 1):
            type_name = type(element).__name__

            if isinstance(element, Task):
                tcode = f" [{element.transaction_code}]" if element.transaction_code else ""
                doc = f"\n     Documentation: {element.documentation}" if element.documentation else ""
                lines.append(f"{i}. [Task]{tcode} {element.name}{doc}")

            elif isinstance(element, Gateway):
                outgoing = process.get_outgoing_flows(element.id)
                paths = []
                for target_id, label in outgoing:
                    target = process.get_element_by_id(target_id)
                    target_name = target.name if target else target_id
                    path_label = f"'{label}'" if label else "default"
                    paths.append(f"  → {path_label} → {target_name}")
                doc = f"\n     Documentation: {element.documentation}" if element.documentation else ""
                lines.append(f"{i}. [Decision: {element.gateway_type}] {element.name}{doc}")
                for path in paths:
                    lines.append(f"   {path}")

            elif isinstance(element, Event):
                lines.append(f"{i}. [{element.event_type.title()} Event] {element.name}")

        return "\n".join(lines) if lines else "(empty process)"

    def _format_decision_points(self, process) -> str:
        """Format decision points with their paths for the prompt."""
        if not process.decision_points:
            return "(no decision points in this process)"

        lines = []
        for gw in process.decision_points:
            lines.append(f"Decision: {gw.name}")
            if gw.documentation:
                lines.append(f"  Criteria: {gw.documentation}")

            outgoing = process.get_outgoing_flows(gw.id)
            for target_id, label in outgoing:
                target = process.get_element_by_id(target_id)
                target_name = target.name if target else target_id
                lines.append(f"  Path: '{label}' → {target_name}")
            lines.append("")

        return "\n".join(lines)
