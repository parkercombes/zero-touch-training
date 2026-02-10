"""
BPMN 2.0 Process Model Parser

Parses BPMN 2.0 XML (as exported from Signavio or similar) into structured
data that the AI content generation layer can use to produce process
explainer videos, role context, and training assembly.

Extracts:
- Process metadata (name, documentation)
- Tasks with role assignments and documentation
- Gateways with decision logic
- Events (start, intermediate, end)
- Sequence flows (process ordering)
- Participants / swimlanes (roles)
- Message flows between participants
- Data objects / documents
"""

from dataclasses import dataclass, field
from typing import Optional
from lxml import etree


BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
BPMNDI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"
DC_NS = "http://www.omg.org/spec/DD/20100524/DC"

NS = {
    "bpmn": BPMN_NS,
    "bpmndi": BPMNDI_NS,
    "dc": DC_NS,
}


@dataclass
class BpmnElement:
    """Base class for BPMN elements."""
    id: str
    name: str
    documentation: str = ""


@dataclass
class Task(BpmnElement):
    """A BPMN task (user task, service task, etc.)."""
    incoming: list[str] = field(default_factory=list)
    outgoing: list[str] = field(default_factory=list)

    @property
    def transaction_code(self) -> str:
        """Extract SAP transaction code from task name if present."""
        # Look for patterns like (ME51N), (MIGO), (MMBE)
        import re
        match = re.search(r'\(([A-Z0-9]{2,10})\)', self.name)
        return match.group(1) if match else ""


@dataclass
class Gateway(BpmnElement):
    """A BPMN gateway (exclusive, parallel, inclusive)."""
    gateway_type: str = ""  # exclusive, parallel, inclusive
    incoming: list[str] = field(default_factory=list)
    outgoing: list[str] = field(default_factory=list)
    default_flow: str = ""


@dataclass
class Event(BpmnElement):
    """A BPMN event (start, intermediate, end)."""
    event_type: str = ""  # start, intermediate, end
    incoming: list[str] = field(default_factory=list)
    outgoing: list[str] = field(default_factory=list)


@dataclass
class SequenceFlow:
    """A sequence flow connecting two BPMN elements."""
    id: str
    name: str
    source_ref: str
    target_ref: str


@dataclass
class Participant:
    """A participant (swimlane/role) in the process."""
    id: str
    name: str
    process_ref: str = ""


@dataclass
class MessageFlow:
    """A message flow between participants."""
    id: str
    name: str
    source_ref: str
    target_ref: str


@dataclass
class DataObject:
    """A data object / document in the process."""
    id: str
    documentation: str = ""


@dataclass
class BpmnProcess:
    """Fully parsed representation of a BPMN process model."""
    id: str
    name: str
    documentation: str = ""
    tasks: list[Task] = field(default_factory=list)
    gateways: list[Gateway] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    sequence_flows: list[SequenceFlow] = field(default_factory=list)
    participants: list[Participant] = field(default_factory=list)
    message_flows: list[MessageFlow] = field(default_factory=list)
    data_objects: list[DataObject] = field(default_factory=list)

    @property
    def roles(self) -> list[str]:
        """List of role names from participants."""
        return [p.name for p in self.participants]

    @property
    def ordered_elements(self) -> list[BpmnElement]:
        """Return process elements in execution order by walking the sequence flows."""
        # Build adjacency from sequence flows
        flow_map: dict[str, list[str]] = {}
        for flow in self.sequence_flows:
            flow_map.setdefault(flow.source_ref, []).append(flow.target_ref)

        # Build element lookup
        elements: dict[str, BpmnElement] = {}
        for task in self.tasks:
            elements[task.id] = task
        for gw in self.gateways:
            elements[gw.id] = gw
        for ev in self.events:
            elements[ev.id] = ev

        # Find start event
        start = None
        for ev in self.events:
            if ev.event_type == "start":
                start = ev
                break

        if not start:
            return list(elements.values())

        # BFS traversal
        ordered = []
        visited = set()
        queue = [start.id]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id in elements:
                ordered.append(elements[current_id])

            for next_id in flow_map.get(current_id, []):
                if next_id not in visited:
                    queue.append(next_id)

        return ordered

    @property
    def decision_points(self) -> list[Gateway]:
        """Return gateways that represent decision points."""
        return [gw for gw in self.gateways if gw.gateway_type == "exclusive"]

    def get_flow_label(self, source_id: str, target_id: str) -> str:
        """Get the label on a sequence flow between two elements."""
        for flow in self.sequence_flows:
            if flow.source_ref == source_id and flow.target_ref == target_id:
                return flow.name
        return ""

    def get_outgoing_flows(self, element_id: str) -> list[tuple[str, str]]:
        """Get (target_id, label) pairs for outgoing flows from an element."""
        results = []
        for flow in self.sequence_flows:
            if flow.source_ref == element_id:
                results.append((flow.target_ref, flow.name))
        return results

    def get_element_by_id(self, element_id: str) -> Optional[BpmnElement]:
        """Look up any element by ID."""
        for task in self.tasks:
            if task.id == element_id:
                return task
        for gw in self.gateways:
            if gw.id == element_id:
                return gw
        for ev in self.events:
            if ev.id == element_id:
                return ev
        return None


class BpmnParser:
    """Parses BPMN 2.0 XML into a structured BpmnProcess object."""

    def parse(self, xml_path: str) -> BpmnProcess:
        """Parse a BPMN 2.0 XML file and return a BpmnProcess."""
        tree = etree.parse(xml_path)
        root = tree.getroot()

        # Get top-level documentation
        doc_text = self._get_documentation(root)

        # Find the process element
        process_el = root.find("bpmn:process", NS)
        if process_el is None:
            raise ValueError(f"No bpmn:process element found in {xml_path}")

        process = BpmnProcess(
            id=process_el.get("id", ""),
            name=process_el.get("name", ""),
            documentation=doc_text or self._get_documentation(process_el),
        )

        # Parse tasks
        for task_el in process_el.findall("bpmn:task", NS):
            process.tasks.append(self._parse_task(task_el))

        # Also check for userTask, serviceTask, etc.
        for tag in ["bpmn:userTask", "bpmn:serviceTask", "bpmn:sendTask", "bpmn:receiveTask"]:
            for task_el in process_el.findall(tag, NS):
                process.tasks.append(self._parse_task(task_el))

        # Parse gateways
        for gw_type, gw_tag in [
            ("exclusive", "bpmn:exclusiveGateway"),
            ("parallel", "bpmn:parallelGateway"),
            ("inclusive", "bpmn:inclusiveGateway"),
        ]:
            for gw_el in process_el.findall(gw_tag, NS):
                process.gateways.append(self._parse_gateway(gw_el, gw_type))

        # Parse events
        for ev_el in process_el.findall("bpmn:startEvent", NS):
            process.events.append(self._parse_event(ev_el, "start"))
        for ev_el in process_el.findall("bpmn:intermediateThrowEvent", NS):
            process.events.append(self._parse_event(ev_el, "intermediate"))
        for ev_el in process_el.findall("bpmn:intermediateCatchEvent", NS):
            process.events.append(self._parse_event(ev_el, "intermediate"))
        for ev_el in process_el.findall("bpmn:endEvent", NS):
            process.events.append(self._parse_event(ev_el, "end"))

        # Parse sequence flows
        for flow_el in process_el.findall("bpmn:sequenceFlow", NS):
            process.sequence_flows.append(SequenceFlow(
                id=flow_el.get("id", ""),
                name=flow_el.get("name", ""),
                source_ref=flow_el.get("sourceRef", ""),
                target_ref=flow_el.get("targetRef", ""),
            ))

        # Parse collaboration (participants, message flows)
        collab_el = root.find("bpmn:collaboration", NS)
        if collab_el is not None:
            for part_el in collab_el.findall("bpmn:participant", NS):
                process.participants.append(Participant(
                    id=part_el.get("id", ""),
                    name=part_el.get("name", ""),
                    process_ref=part_el.get("processRef", ""),
                ))
            for mf_el in collab_el.findall("bpmn:messageFlow", NS):
                process.message_flows.append(MessageFlow(
                    id=mf_el.get("id", ""),
                    name=mf_el.get("name", ""),
                    source_ref=mf_el.get("sourceRef", ""),
                    target_ref=mf_el.get("targetRef", ""),
                ))

        # Parse data objects (itemDefinitions with documentation)
        for item_el in root.findall("bpmn:itemDefinition", NS):
            doc = self._get_documentation(item_el)
            if doc:
                process.data_objects.append(DataObject(
                    id=item_el.get("id", ""),
                    documentation=doc,
                ))

        return process

    def _parse_task(self, task_el) -> Task:
        """Parse a BPMN task element."""
        return Task(
            id=task_el.get("id", ""),
            name=task_el.get("name", ""),
            documentation=self._get_documentation(task_el),
            incoming=[el.text for el in task_el.findall("bpmn:incoming", NS) if el.text],
            outgoing=[el.text for el in task_el.findall("bpmn:outgoing", NS) if el.text],
        )

    def _parse_gateway(self, gw_el, gw_type: str) -> Gateway:
        """Parse a BPMN gateway element."""
        return Gateway(
            id=gw_el.get("id", ""),
            name=gw_el.get("name", ""),
            gateway_type=gw_type,
            documentation=self._get_documentation(gw_el),
            incoming=[el.text for el in gw_el.findall("bpmn:incoming", NS) if el.text],
            outgoing=[el.text for el in gw_el.findall("bpmn:outgoing", NS) if el.text],
            default_flow=gw_el.get("default", ""),
        )

    def _parse_event(self, ev_el, ev_type: str) -> Event:
        """Parse a BPMN event element."""
        return Event(
            id=ev_el.get("id", ""),
            name=ev_el.get("name", ""),
            event_type=ev_type,
            documentation=self._get_documentation(ev_el),
            incoming=[el.text for el in ev_el.findall("bpmn:incoming", NS) if el.text],
            outgoing=[el.text for el in ev_el.findall("bpmn:outgoing", NS) if el.text],
        )

    @staticmethod
    def _get_documentation(element) -> str:
        """Extract documentation text from a BPMN element."""
        doc_el = element.find("bpmn:documentation", NS)
        if doc_el is not None:
            text_el = doc_el.find("bpmn:text", NS)
            if text_el is not None and text_el.text:
                return text_el.text.strip()
            if doc_el.text:
                return doc_el.text.strip()
        return ""


def summarize(process: BpmnProcess) -> str:
    """Generate a human-readable summary of a parsed BPMN process."""
    lines = [
        f"Process: {process.name}",
        f"  ID: {process.id}",
        f"  Roles: {', '.join(process.roles)}",
        f"  Tasks: {len(process.tasks)}",
        f"  Gateways: {len(process.gateways)}",
        f"  Events: {len(process.events)}",
        f"  Flows: {len(process.sequence_flows)}",
        "",
    ]

    if process.documentation:
        lines.append("Documentation:")
        for doc_line in process.documentation.split("\n")[:8]:
            lines.append(f"  {doc_line.strip()}")
        lines.append("")

    lines.append("Process Flow (execution order):")
    for element in process.ordered_elements:
        type_label = type(element).__name__
        extra = ""
        if isinstance(element, Task) and element.transaction_code:
            extra = f" [{element.transaction_code}]"
        elif isinstance(element, Gateway):
            outgoing = process.get_outgoing_flows(element.id)
            paths = [f"'{label}'" if label else "default" for _, label in outgoing]
            extra = f" → paths: {', '.join(paths)}" if paths else ""
        lines.append(f"  [{type_label:8s}] {element.name}{extra}")

    if process.decision_points:
        lines.append("")
        lines.append("Decision Points:")
        for gw in process.decision_points:
            lines.append(f"  {gw.name}")
            if gw.documentation:
                for doc_line in gw.documentation.split("\n")[:4]:
                    lines.append(f"    {doc_line.strip()}")

    if process.data_objects:
        lines.append("")
        lines.append("Key Documents:")
        for obj in process.data_objects:
            first_line = obj.documentation.split("\n")[0] if obj.documentation else obj.id
            lines.append(f"  - {first_line}")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python bpmn_parser.py <path_to_bpmn_xml>")
        sys.exit(1)

    parser = BpmnParser()
    process = parser.parse(sys.argv[1])
    print(summarize(process))
