"""
Opal Overlay Assembler

Implements the Opal overlay pattern:
  Enterprise baseline + Site-specific overlay + Role context = Delivered training

This module:
1. Loads the Opal overlay YAML for a site
2. Matches overlay rules to parsed Tosca/BPMN data by transaction code
3. Enriches parsed data with site-specific constraints
4. Provides the resolved overlay data to generators for prompt injection

The overlay doesn't modify the parsed data structures — it provides a parallel
"site lens" that generators use to add site-specific callouts, warnings, and
variations to the training content.
"""

from pathlib import Path
import yaml


class OpalOverlayAssembler:
    """Loads and resolves Opal site-specific overlays."""

    def __init__(self, overlay_paths: list[str]):
        """
        Initialize with one or more overlay YAML files.

        Args:
            overlay_paths: List of paths to Opal overlay YAML files
        """
        self.overlay_paths = [Path(p) for p in overlay_paths]
        self.raw_overlays: list[dict] = []
        self.site_info: dict = {}

    def load(self) -> None:
        """Load all overlay YAML files."""
        for path in self.overlay_paths:
            if not path.exists():
                print(f"  ⚠️  Overlay file not found: {path}")
                continue

            with open(path, "r") as f:
                data = yaml.safe_load(f)

            if data:
                # Extract site metadata
                if "site" in data:
                    self.site_info = data["site"]

                # Collect overlays
                if "overlays" in data:
                    self.raw_overlays.extend(data["overlays"])

            print(f"  ✅ Loaded overlay: {path.name} "
                  f"({len(data.get('overlays', []))} rules)")

    def resolve(self, role: str = "") -> dict:
        """
        Resolve overlays into a structured dict that generators can consume.

        Optionally filters by role relevance.

        Args:
            role: Target role (e.g., 'Buyer') — currently used for
                  future role-based filtering

        Returns:
            Dict with 'site', 'overlays' keys ready for generator consumption
        """
        resolved = {
            "site": self.site_info,
            "overlays": [],
        }

        for overlay in self.raw_overlays:
            resolved_overlay = {
                "process": overlay.get("process", ""),
                "transaction": overlay.get("transaction", ""),
                "variations": [],
            }

            for variation in overlay.get("variations", []):
                resolved_variation = {
                    "type": variation.get("type", ""),
                    "enterprise_default": variation.get("enterprise_default", ""),
                    "site_override": variation.get("site_override", ""),
                    "reason": variation.get("reason", ""),
                }

                # Field-based variation
                if "field" in variation:
                    resolved_variation["field"] = variation["field"]
                    resolved_variation["field_technical"] = variation.get("field_technical", "")

                # Step-based variation
                if "step" in variation:
                    resolved_variation["step"] = variation["step"]

                # Approval tier details
                if "tiers" in variation:
                    resolved_variation["tiers"] = variation["tiers"]

                # Process gate conditions
                if "condition" in variation:
                    resolved_variation["condition"] = variation["condition"]

                # Process gate actions
                if "actions" in variation:
                    resolved_variation["actions"] = variation["actions"]

                # Temperature ranges
                if "temperature_ranges" in variation:
                    resolved_variation["temperature_ranges"] = variation["temperature_ranges"]

                resolved_overlay["variations"].append(resolved_variation)

            resolved["overlays"].append(resolved_overlay)

        return resolved

    def get_overlays_for_transaction(self, transaction_code: str) -> list[dict]:
        """
        Get overlay variations for a specific transaction code.

        Args:
            transaction_code: SAP transaction code (e.g., 'ME51N')

        Returns:
            List of variation dicts for that transaction
        """
        results = []
        for overlay in self.raw_overlays:
            if overlay.get("transaction", "") == transaction_code:
                results.extend(overlay.get("variations", []))
        return results

    def get_field_constraints(self, transaction_code: str) -> list[dict]:
        """Get field-level constraints for a transaction."""
        return [
            v for v in self.get_overlays_for_transaction(transaction_code)
            if "field" in v
        ]

    def get_process_gates(self, transaction_code: str) -> list[dict]:
        """Get process gate rules for a transaction."""
        return [
            v for v in self.get_overlays_for_transaction(transaction_code)
            if v.get("type") == "process_gate"
        ]

    def get_approval_rules(self, transaction_code: str) -> list[dict]:
        """Get approval rules for a transaction."""
        return [
            v for v in self.get_overlays_for_transaction(transaction_code)
            if v.get("type") == "approval_rule"
        ]

    def summary(self) -> str:
        """Return a human-readable summary of loaded overlays."""
        lines = [
            f"Site: {self.site_info.get('name', 'Unknown')} ({self.site_info.get('code', '')})",
            f"System: {self.site_info.get('system', '')}",
            f"Total overlay rules: {sum(len(o.get('variations', [])) for o in self.raw_overlays)}",
            "",
        ]
        for overlay in self.raw_overlays:
            process = overlay.get("process", "")
            txn = overlay.get("transaction", "")
            variations = overlay.get("variations", [])
            lines.append(f"  {process} ({txn}): {len(variations)} variations")
            for v in variations:
                label = v.get("field", v.get("step", ""))
                v_type = v.get("type", "")
                lines.append(f"    - {label} [{v_type}]")
        return "\n".join(lines)
