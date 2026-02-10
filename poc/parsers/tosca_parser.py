"""
Tosca Test Script Parser

Parses Tosca-style XML test scripts into structured data that the AI content
generation layer can use to produce training materials.

Extracts:
- Test metadata (name, process, transaction, site, execution status)
- Ordered test steps with actions, UI elements, values, assertions
- Site-specific annotations (Anniston constraints)
- Test data sets
"""

from dataclasses import dataclass, field
from typing import Optional
from lxml import etree


@dataclass
class Assertion:
    """A validation assertion on a test step."""
    type: str
    field_reference: str = ""
    expected_value: str = ""
    allowed_values: str = ""
    validation_type: str = ""
    reason: str = ""


@dataclass
class UIElement:
    """A reference to a UI element targeted by a test step."""
    identifier: str
    description: str = ""


@dataclass
class TestStep:
    """A single step in a Tosca test script."""
    step_id: str
    step_number: int
    description: str
    action_type: str  # NAVIGATE, CLICK, INPUT, SELECT, VERIFY, CALCULATE
    element: Optional[UIElement] = None
    value: str = ""
    target_url: str = ""
    expected_result: str = ""
    screenshot: str = ""
    assertions: list[Assertion] = field(default_factory=list)

    @property
    def is_user_action(self) -> bool:
        """Returns True if this step is something a user would perform (not just verification)."""
        return self.action_type in ("NAVIGATE", "CLICK", "INPUT", "SELECT")

    @property
    def is_verification(self) -> bool:
        """Returns True if this step is a verification/assertion check."""
        return self.action_type in ("VERIFY", "CALCULATE")


@dataclass
class Annotation:
    """A site-specific annotation on the test script."""
    type: str
    step_id: str = ""
    description: str = ""


@dataclass
class TestDataRow:
    """A single field in the test data set."""
    field_name: str
    field_value: str
    field_description: str = ""


@dataclass
class ToscaTestScript:
    """Fully parsed representation of a Tosca test script."""
    script_id: str
    name: str
    description: str
    version: str
    process: str = ""
    transaction: str = ""
    site_code: str = ""
    site_name: str = ""
    system_name: str = ""
    execution_status: str = ""
    execution_count: int = 0
    last_executed: str = ""
    steps: list[TestStep] = field(default_factory=list)
    annotations: list[Annotation] = field(default_factory=list)
    test_data: list[TestDataRow] = field(default_factory=list)

    @property
    def user_action_steps(self) -> list[TestStep]:
        """Returns only the steps a user would perform (excludes verifications)."""
        return [s for s in self.steps if s.is_user_action]

    @property
    def site_specific_annotations(self) -> list[Annotation]:
        """Returns only site-specific constraint annotations."""
        return [a for a in self.annotations if "SPECIFIC" in a.type.upper()]

    @property
    def site_specific_steps(self) -> list[TestStep]:
        """Returns steps that have site-specific assertions (FIELD_REQUIRED, ALLOWED_VALUES, etc.)."""
        site_step_ids = {a.step_id for a in self.site_specific_annotations}
        result = []
        for step in self.steps:
            if step.step_id in site_step_ids:
                result.append(step)
                continue
            for assertion in step.assertions:
                if assertion.reason and ("anniston" in assertion.reason.lower() or "site" in assertion.reason.lower()):
                    result.append(step)
                    break
        return result


class ToscaParser:
    """Parses Tosca-style XML test scripts into structured ToscaTestScript objects."""

    TOSCA_NS = "http://www.tricentis.com/tosca/2.0"

    def __init__(self):
        self.ns = {"t": self.TOSCA_NS}

    def parse(self, xml_path: str) -> ToscaTestScript:
        """Parse a Tosca XML file and return a ToscaTestScript."""
        tree = etree.parse(xml_path)
        root = tree.getroot()

        # Detect namespace usage
        if root.tag.startswith("{"):
            return self._parse_with_namespace(root)
        else:
            return self._parse_without_namespace(root)

    def _parse_with_namespace(self, root) -> ToscaTestScript:
        """Parse XML that uses the Tosca namespace."""
        ns = self.ns

        metadata = root.find("t:Metadata", ns)
        env = root.find("t:TestEnvironment", ns)

        script = ToscaTestScript(
            script_id=self._text(metadata, "t:TestScriptId", ns),
            name=self._text(metadata, "t:Name", ns),
            description=self._text(metadata, "t:Description", ns),
            version=self._text(metadata, "t:Version", ns),
            execution_status=self._text(metadata, "t:ExecutionStatus", ns),
            execution_count=int(self._text(metadata, "t:ExecutionCount", ns) or "0"),
            last_executed=self._text(metadata, "t:LastExecutedDate", ns),
            site_code=self._text(env, "t:SiteCode", ns) if env is not None else "",
            site_name=self._text(env, "t:SiteName", ns) if env is not None else "",
            system_name=self._text(env, "t:SystemName", ns) if env is not None else "",
        )

        # Parse steps
        for step_el in root.findall(".//t:Step", ns):
            script.steps.append(self._parse_step_ns(step_el, ns))

        # Parse annotations
        for ann_el in root.findall(".//t:Annotation", ns):
            script.annotations.append(Annotation(
                type=self._text(ann_el, "t:Type", ns),
                step_id=self._text(ann_el, "t:Step", ns),
                description=self._text(ann_el, "t:Description", ns),
            ))

        # Parse test data
        for row_el in root.findall(".//t:DataRow", ns):
            script.test_data.append(TestDataRow(
                field_name=self._text(row_el, "t:FieldName", ns),
                field_value=self._text(row_el, "t:FieldValue", ns),
                field_description=self._text(row_el, "t:FieldDescription", ns),
            ))

        return script

    def _parse_step_ns(self, step_el, ns) -> TestStep:
        """Parse a single test step with namespace."""
        action_el = step_el.find("t:Action", ns)
        action_type = self._text(action_el, "t:Type", ns) if action_el is not None else ""

        # Parse UI element
        element = None
        elem_el = action_el.find("t:Element", ns) if action_el is not None else None
        if elem_el is not None:
            element = UIElement(
                identifier=self._text(elem_el, "t:Identifier", ns),
                description=self._text(elem_el, "t:Description", ns),
            )

        # Parse value
        value = self._text(action_el, "t:Value", ns) if action_el is not None else ""

        # Parse target URL
        target_url = self._text(action_el, "t:TargetURL", ns) if action_el is not None else ""

        # Parse assertions
        assertions = []
        for assert_el in step_el.findall("t:Assertion", ns):
            assertions.append(Assertion(
                type=self._text(assert_el, "t:Type", ns),
                field_reference=self._text(assert_el, "t:FieldReference", ns),
                expected_value=self._text(assert_el, "t:ExpectedValue", ns),
                allowed_values=self._text(assert_el, "t:AllowedValues", ns),
                validation_type=self._text(assert_el, "t:ValidationType", ns),
                reason=self._text(assert_el, "t:Reason", ns),
            ))

        return TestStep(
            step_id=self._text(step_el, "t:StepId", ns),
            step_number=int(self._text(step_el, "t:StepNumber", ns) or "0"),
            description=self._text(step_el, "t:Description", ns),
            action_type=action_type,
            element=element,
            value=value,
            target_url=target_url,
            expected_result=self._text(step_el, "t:ExpectedResult", ns),
            screenshot=self._text(step_el, "t:ScreenshotReference", ns),
            assertions=assertions,
        )

    def _parse_without_namespace(self, root) -> ToscaTestScript:
        """Parse XML that does not use namespaces (fallback)."""
        metadata = root.find("Metadata") or root.find("metadata")
        env = root.find("TestEnvironment") or root.find("testEnvironment")

        script = ToscaTestScript(
            script_id=self._text_plain(metadata, "TestScriptId"),
            name=self._text_plain(metadata, "Name") or self._text_plain(metadata, "name"),
            description=self._text_plain(metadata, "Description") or self._text_plain(metadata, "description"),
            version=self._text_plain(metadata, "Version") or self._text_plain(metadata, "version"),
            execution_status=self._text_plain(metadata, "ExecutionStatus") or self._text_plain(metadata, "status"),
            execution_count=int(self._text_plain(metadata, "ExecutionCount") or "0"),
            last_executed=self._text_plain(metadata, "LastExecutedDate") or self._text_plain(metadata, "last_executed"),
            site_code=self._text_plain(env, "SiteCode") if env is not None else "",
            site_name=self._text_plain(env, "SiteName") if env is not None else "",
            system_name=self._text_plain(env, "SystemName") if env is not None else "",
        )

        # Parse steps
        steps_container = root.find(".//TestSteps") or root.find(".//steps")
        if steps_container is not None:
            for step_el in steps_container.findall("Step") or steps_container.findall("step"):
                script.steps.append(self._parse_step_plain(step_el))

        # Parse annotations
        annotations_container = root.find(".//Annotations")
        if annotations_container is not None:
            for ann_el in annotations_container.findall("Annotation"):
                script.annotations.append(Annotation(
                    type=self._text_plain(ann_el, "Type"),
                    step_id=self._text_plain(ann_el, "Step"),
                    description=self._text_plain(ann_el, "Description"),
                ))

        # Parse test data
        for row_el in root.findall(".//DataRow"):
            script.test_data.append(TestDataRow(
                field_name=self._text_plain(row_el, "FieldName"),
                field_value=self._text_plain(row_el, "FieldValue"),
                field_description=self._text_plain(row_el, "FieldDescription"),
            ))

        return script

    def _parse_step_plain(self, step_el) -> TestStep:
        """Parse a single test step without namespace."""
        action_el = step_el.find("Action")
        action_type = self._text_plain(action_el, "Type") if action_el is not None else ""

        element = None
        elem_el = action_el.find("Element") if action_el is not None else None
        if elem_el is not None:
            element = UIElement(
                identifier=self._text_plain(elem_el, "Identifier"),
                description=self._text_plain(elem_el, "Description"),
            )

        value = self._text_plain(action_el, "Value") if action_el is not None else ""
        target_url = self._text_plain(action_el, "TargetURL") if action_el is not None else ""

        assertions = []
        for assert_el in step_el.findall("Assertion"):
            assertions.append(Assertion(
                type=self._text_plain(assert_el, "Type"),
                field_reference=self._text_plain(assert_el, "FieldReference"),
                expected_value=self._text_plain(assert_el, "ExpectedValue"),
                allowed_values=self._text_plain(assert_el, "AllowedValues"),
                validation_type=self._text_plain(assert_el, "ValidationType"),
                reason=self._text_plain(assert_el, "Reason"),
            ))

        return TestStep(
            step_id=self._text_plain(step_el, "StepId"),
            step_number=int(self._text_plain(step_el, "StepNumber") or "0"),
            description=self._text_plain(step_el, "Description"),
            action_type=action_type,
            element=element,
            value=value,
            target_url=target_url,
            expected_result=self._text_plain(step_el, "ExpectedResult"),
            screenshot=self._text_plain(step_el, "ScreenshotReference"),
            assertions=assertions,
        )

    @staticmethod
    def _text(parent, tag: str, ns: dict) -> str:
        """Extract text from a namespaced child element."""
        if parent is None:
            return ""
        el = parent.find(tag, ns)
        return (el.text or "").strip() if el is not None else ""

    @staticmethod
    def _text_plain(parent, tag: str) -> str:
        """Extract text from a non-namespaced child element."""
        if parent is None:
            return ""
        el = parent.find(tag)
        return (el.text or "").strip() if el is not None else ""


def summarize(script: ToscaTestScript) -> str:
    """Generate a human-readable summary of a parsed test script."""
    lines = [
        f"Test Script: {script.name}",
        f"  ID: {script.script_id}",
        f"  Site: {script.site_name} ({script.site_code})",
        f"  System: {script.system_name}",
        f"  Status: {script.execution_status} ({script.execution_count} runs)",
        f"  Last Run: {script.last_executed}",
        f"  Total Steps: {len(script.steps)}",
        f"  User Action Steps: {len(script.user_action_steps)}",
        f"  Site-Specific Steps: {len(script.site_specific_steps)}",
        "",
        "Steps:",
    ]
    for step in script.steps:
        marker = " [SITE-SPECIFIC]" if step in script.site_specific_steps else ""
        action_detail = ""
        if step.value:
            action_detail = f" → {step.value}"
        elif step.target_url:
            action_detail = f" → {step.target_url}"
        lines.append(f"  {step.step_number:3d}. [{step.action_type:8s}] {step.description}{action_detail}{marker}")

    if script.annotations:
        lines.append("")
        lines.append("Annotations:")
        for ann in script.annotations:
            lines.append(f"  [{ann.type}] {ann.description[:100]}...")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tosca_parser.py <path_to_tosca_xml>")
        sys.exit(1)

    parser = ToscaParser()
    script = parser.parse(sys.argv[1])
    print(summarize(script))
