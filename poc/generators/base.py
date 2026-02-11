"""
Base Generator

Shared logic for all AI content generators:
- Claude API interaction (via urllib — no SDK dependency needed)
- Prompt template loading and rendering
- Output file writing
- Error handling and retries
"""

import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path


class BaseGenerator:
    """Base class for AI training content generators."""

    # Subclasses set these
    PROMPT_TEMPLATE: str = ""  # filename in prompts/ dir
    OUTPUT_SUBDIR: str = ""    # subdirectory under output/
    OUTPUT_EXT: str = ".md"    # output file extension

    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def __init__(self, config: dict, output_dir: str = "output"):
        """
        Initialize the generator.

        Args:
            config: Parsed config.yaml as dict
            output_dir: Base output directory
        """
        self.config = config
        self.scope = config.get("scope", {})
        self.output_dir = Path(output_dir)
        self.prompts_dir = Path(__file__).parent.parent / "prompts"

        # Get API key
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
            )
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    def load_template(self) -> str:
        """Load the prompt template from the prompts directory."""
        template_path = self.prompts_dir / self.PROMPT_TEMPLATE
        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")
        return template_path.read_text()

    def render_prompt(self, template: str, variables: dict) -> str:
        """
        Render a prompt template with variables.

        Uses str.format_map with a defaultdict to leave unresolved
        placeholders intact rather than crashing.
        """
        class DefaultDict(dict):
            def __missing__(self, key):
                return f"{{{key}}}"

        return template.format_map(DefaultDict(**variables))

    def call_claude(self, prompt: str, max_tokens: int = 4096) -> str:
        """
        Send a prompt to Claude via the REST API and return the response text.

        Uses urllib directly so there's no dependency on the anthropic SDK.
        Includes retry logic for transient API errors.
        """
        payload = json.dumps({
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }).encode("utf-8")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json",
        }

        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    self.API_URL,
                    method="POST",
                    headers=headers,
                    data=payload,
                )
                resp = urllib.request.urlopen(req, timeout=120)
                body = json.loads(resp.read().decode("utf-8"))

                # Extract text from response content blocks
                text_parts = []
                for block in body.get("content", []):
                    if block.get("type") == "text":
                        text_parts.append(block["text"])
                return "\n".join(text_parts)

            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8", errors="replace")
                try:
                    error_data = json.loads(error_body)
                    error_msg = error_data.get("error", {}).get("message", error_body)
                except json.JSONDecodeError:
                    error_msg = error_body

                if attempt < 2 and e.code in (429, 500, 502, 503, 529):
                    wait = 2 ** attempt
                    print(f"  ⚠️  API error {e.code} (attempt {attempt + 1}/3): {error_msg}")
                    print(f"  Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(
                        f"Claude API call failed (HTTP {e.code}): {error_msg}"
                    )

            except Exception as e:
                if attempt < 2:
                    wait = 2 ** attempt
                    print(f"  ⚠️  API error (attempt {attempt + 1}/3): {e}")
                    print(f"  Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(
                        f"Claude API call failed after 3 attempts: {e}"
                    ) from e

    def write_output(self, content: str, filename: str) -> Path:
        """
        Write generated content to the output directory.

        Returns the path to the written file.
        """
        # Create output subdirectory if needed
        out_dir = self.output_dir
        if self.OUTPUT_SUBDIR:
            out_dir = out_dir / self.OUTPUT_SUBDIR
        out_dir.mkdir(parents=True, exist_ok=True)

        # Write file
        out_path = out_dir / filename
        out_path.write_text(content, encoding="utf-8")
        return out_path

    def generate(self, parsed_data: dict, overlay_data: dict) -> Path:
        """
        Main generation method. Subclasses must implement this.

        Args:
            parsed_data: Dict with 'tosca_scripts' and/or 'bpmn_processes' keys
            overlay_data: Resolved overlay data from the assembler

        Returns:
            Path to the generated output file
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def _format_steps_for_prompt(self, steps) -> str:
        """Format test steps into a readable string for prompt injection."""
        lines = []
        for step in steps:
            line = f"Step {step.step_number}: [{step.action_type}] {step.description}"
            if step.element:
                line += f"\n  UI Element: {step.element.identifier}"
                if step.element.description:
                    line += f" ({step.element.description})"
            if step.value:
                line += f"\n  Value: {step.value}"
            if step.target_url:
                line += f"\n  Navigate to: {step.target_url}"
            if step.expected_result:
                line += f"\n  Expected: {step.expected_result}"
            if step.assertions:
                for a in step.assertions:
                    parts = [f"  Assertion [{a.type}]"]
                    if a.field_reference:
                        parts.append(f"Field: {a.field_reference}")
                    if a.expected_value:
                        parts.append(f"Expected: {a.expected_value}")
                    if a.allowed_values:
                        parts.append(f"Allowed: {a.allowed_values}")
                    if a.reason:
                        parts.append(f"Reason: {a.reason}")
                    line += "\n  " + " | ".join(parts)
            lines.append(line)
        return "\n\n".join(lines)

    def _format_test_data_for_prompt(self, test_data) -> str:
        """Format test data rows into a readable string."""
        if not test_data:
            return "(no test data available)"
        lines = []
        for row in test_data:
            desc = f" — {row.field_description}" if row.field_description else ""
            lines.append(f"- {row.field_name}: {row.field_value}{desc}")
        return "\n".join(lines)

    def _format_site_constraints(self, overlay_data: dict) -> str:
        """Format overlay constraints into a readable string for prompts."""
        if not overlay_data or "overlays" not in overlay_data:
            return "(no site-specific constraints)"
        lines = []
        for overlay in overlay_data.get("overlays", []):
            process = overlay.get("process", "")
            transaction = overlay.get("transaction", "")
            lines.append(f"\nProcess: {process} ({transaction})")
            for variation in overlay.get("variations", []):
                v_type = variation.get("type", "")
                if "field" in variation:
                    field = variation["field"]
                    enterprise = variation.get("enterprise_default", "")
                    site = variation.get("site_override", "")
                    reason = variation.get("reason", "")
                    lines.append(f"  ⚠️ {field} [{v_type}]")
                    lines.append(f"     Enterprise default: {enterprise}")
                    lines.append(f"     Site override: {site}")
                    lines.append(f"     Reason: {reason}")
                elif "step" in variation:
                    step = variation["step"]
                    enterprise = variation.get("enterprise_default", "")
                    site = variation.get("site_override", "")
                    reason = variation.get("reason", "")
                    lines.append(f"  ⚠️ {step} [{v_type}]")
                    lines.append(f"     Enterprise default: {enterprise}")
                    lines.append(f"     Site override: {site}")
                    lines.append(f"     Reason: {reason}")
        return "\n".join(lines) if lines else "(no site-specific constraints)"

    def _get_scope_vars(self) -> dict:
        """Get common scope variables from config."""
        return {
            "company": self.scope.get("company", ""),
            "site_name": self.scope.get("site", ""),
            "site_code": self.scope.get("site_code", ""),
            "system_name": self.scope.get("system", ""),
            "process_name": self.scope.get("process", ""),
            "role": self.scope.get("role", ""),
            "date": time.strftime("%Y-%m-%d"),
        }
