"""
Security Module

Data protection, classification, and anonymization.
"""

import re
from enum import Enum
from typing import Dict, Tuple


class SensitivityLevel(str, Enum):
    """Data sensitivity levels."""
    PUBLIC = "PUBLIC"           # Can be sent to any cloud AI
    INTERNAL = "INTERNAL"       # Trusted cloud AI only (Claude, Azure)
    CONFIDENTIAL = "CONFIDENTIAL"  # Local AI only OR anonymized
    SECRET = "SECRET"           # NEVER sent to AI


# Patterns for detecting sensitive data
SENSITIVE_PATTERNS = {
    "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "api_key": r'(sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36})',
    "phone": r'\+?1?\d{9,15}',
    "ssn": r'\d{3}-\d{2}-\d{4}',
    "credit_card": r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}',
    "password": r'(password|passwd|pwd)\s*[:=]\s*\S+',
    "jwt": r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
}


class DataClassifier:
    """Classifies data sensitivity and detects sensitive patterns."""

    def __init__(self):
        self.patterns = {k: re.compile(v, re.IGNORECASE) for k, v in SENSITIVE_PATTERNS.items()}

    def classify(self, content: str) -> Tuple[SensitivityLevel, Dict[str, int]]:
        """
        Classify content sensitivity and detect patterns.

        Returns:
            Tuple of (sensitivity_level, dict of pattern_name -> count)
        """
        detections = {}
        for name, pattern in self.patterns.items():
            matches = pattern.findall(content)
            if matches:
                detections[name] = len(matches)

        # Determine level based on detections
        if "api_key" in detections or "password" in detections or "jwt" in detections:
            return SensitivityLevel.SECRET, detections
        elif "ssn" in detections or "credit_card" in detections:
            return SensitivityLevel.CONFIDENTIAL, detections
        elif "email" in detections or "phone" in detections:
            return SensitivityLevel.INTERNAL, detections

        return SensitivityLevel.PUBLIC, detections


class DataAnonymizer:
    """Anonymizes sensitive data before sending to AI providers."""

    def __init__(self):
        self.classifier = DataClassifier()
        self.mapping: Dict[str, str] = {}
        self.reverse_mapping: Dict[str, str] = {}
        self.counters: Dict[str, int] = {}

    def anonymize(self, content: str) -> str:
        """Replace sensitive data with placeholders."""
        result = content

        for name, pattern in self.classifier.patterns.items():
            for match in pattern.finditer(content):
                original = match.group()
                if original not in self.mapping:
                    # Generate placeholder
                    if name not in self.counters:
                        self.counters[name] = 0
                    self.counters[name] += 1
                    placeholder = f"[{name.upper()}_{self.counters[name]}]"
                    self.mapping[original] = placeholder
                    self.reverse_mapping[placeholder] = original

                result = result.replace(original, self.mapping[original])

        return result

    def deanonymize(self, content: str) -> str:
        """Restore original values from placeholders."""
        result = content
        for placeholder, original in self.reverse_mapping.items():
            result = result.replace(placeholder, original)
        return result

    def clear(self):
        """Clear all mappings."""
        self.mapping.clear()
        self.reverse_mapping.clear()
        self.counters.clear()
