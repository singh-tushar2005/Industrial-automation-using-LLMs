"""Semantic context for coordinated industrial pipeline analysis.

Wraps classifier output and exposes intent-aware boolean flags that
downstream extractors (RelationshipExtractor, OperationExtractor) can
consume to adjust their behavior.
"""

# Classification tag constants (copied here to avoid circular import)
STATE_MACHINE = "STATE_MACHINE"
PROCESS_SEQUENCING = "PROCESS_SEQUENCING"
CONTROLLED_STARTUP_SEQUENCE = "CONTROLLED_STARTUP_SEQUENCE"
ACTUATOR_COORDINATION = "ACTUATOR_COORDINATION"
MULTI_ACTUATOR_SEQUENCE = "MULTI_ACTUATOR_SEQUENCE"
PROCESS_MONITORING = "PROCESS_MONITORING"
PROCESS_LIMIT_PROTECTION = "PROCESS_LIMIT_PROTECTION"
PROCESS_CONTROL = "PROCESS_CONTROL"
FB_COORDINATION = "FB_COORDINATION"
TIMER_DEPENDENT_CONTROL = "TIMER_DEPENDENT_CONTROL"
MODE_SELECTION_LOGIC = "MODE_SELECTION_LOGIC"


class SemanticContext:
    """Intent-aware context produced by the classifier.

    Backward-compatible with the old dict-based classification report:
    findings, tags, and finding_count are accessible via dict-style keys.
    """

    def __init__(self, findings, tags, type_report=None):
        self._classifications = {
            "findings": list(findings),
            "tags": list(tags),
            "finding_count": len(findings),
        }
        self.findings = list(findings)
        self.tags = set(tags)
        self.type_report = type_report or {}
        self._compute_flags()

    def _compute_flags(self):
        """Derive boolean intent flags from classification tags."""
        self.state_machine_detected = STATE_MACHINE in self.tags
        self.process_sequencing_detected = (
            PROCESS_SEQUENCING in self.tags
            or CONTROLLED_STARTUP_SEQUENCE in self.tags
            or MODE_SELECTION_LOGIC in self.tags
        )
        self.actuator_coordination_detected = (
            ACTUATOR_COORDINATION in self.tags
            or MULTI_ACTUATOR_SEQUENCE in self.tags
        )
        self.measurement_system_detected = (
            PROCESS_MONITORING in self.tags
            or PROCESS_LIMIT_PROTECTION in self.tags
        )
        self.data_processing_detected = (
            FB_COORDINATION in self.tags
            or PROCESS_CONTROL in self.tags
            or not (self.state_machine_detected or self.actuator_coordination_detected)
        )
        self.signal_processing_detected = False

    # ------------------------------------------------------------------
    # Dict compatibility
    # ------------------------------------------------------------------

    def get(self, key, default=None):
        return self._classifications.get(key, default)

    def __getitem__(self, key):
        return self._classifications[key]

    def __contains__(self, key):
        return key in self._classifications

    def to_dict(self):
        return {
            "findings": self.findings,
            "tags": sorted(self.tags),
            "finding_count": len(self.findings),
            "state_machine_detected": self.state_machine_detected,
            "process_sequencing_detected": self.process_sequencing_detected,
            "actuator_coordination_detected": self.actuator_coordination_detected,
            "measurement_system_detected": self.measurement_system_detected,
            "data_processing_detected": self.data_processing_detected,
            "signal_processing_detected": self.signal_processing_detected,
        }
