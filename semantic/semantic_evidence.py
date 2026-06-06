"""Semantic evidence container for pattern library output.

Diagnostic-only module.
"""


try:
    from semantic.pattern_library import PatternLibrary
except ModuleNotFoundError:
    from pattern_library import PatternLibrary


class SemanticEvidence:
    """Container for detected semantic patterns and their confidence scores."""

    def __init__(self, detected_patterns=None):
        self.detected_patterns = detected_patterns or []

    def to_dict(self):
        industrial = [m for m in self.detected_patterns if m.semantic_scope == "INDUSTRIAL"]
        test = [m for m in self.detected_patterns if m.semantic_scope == "TEST"]
        return {
            "detected_patterns": [m.to_dict() for m in self.detected_patterns],
            "pattern_count": len(self.detected_patterns),
            "pattern_frequencies": self._compute_frequencies(),
            "average_confidence": self._compute_avg_confidence(),
            "industrial_patterns": [m.to_dict() for m in industrial],
            "industrial_pattern_count": len(industrial),
            "industrial_pattern_frequencies": dict(Counter(m.pattern_name for m in industrial)),
            "industrial_average_confidence": self._compute_avg_confidence(industrial),
            "test_patterns": [m.to_dict() for m in test],
            "test_pattern_count": len(test),
            "test_pattern_frequencies": dict(Counter(m.pattern_name for m in test)),
            "test_average_confidence": self._compute_avg_confidence(test),
        }

    def _compute_frequencies(self):
        from collections import Counter
        return dict(Counter(m.pattern_name for m in self.detected_patterns))

    def _compute_avg_confidence(self, patterns=None):
        scores = {"low": 0.33, "medium": 0.66, "high": 1.0}
        if patterns is None:
            patterns = self.detected_patterns
        if not patterns:
            return 0.0
        total = sum(scores.get(m.confidence, 0.5) for m in patterns)
        return round(total / len(patterns), 3)


class SemanticEvidenceExtractor:
    """Extract semantic evidence from an AST using the PatternLibrary."""

    def __init__(self):
        self.library = PatternLibrary()

    def extract(self, ast):
        matches = self.library.detect(ast)
        return SemanticEvidence(matches)
