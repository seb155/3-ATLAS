"""
Rule Engine Data Models

Defines the database models for the hierarchical rule system.
Rules are database-driven and support priority-based execution.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class RuleSource(str, enum.Enum):
    """
    Source hierarchy for rules.

    Priority order (from lowest to highest):
    - FIRM (10): Baseline engineering standards
    - COUNTRY (30): Country-specific codes and standards
    - PROJECT (50): Project-specific requirements
    - CLIENT (100): Client preferences (highest priority, overrides all)
    """

    FIRM = "FIRM"
    COUNTRY = "COUNTRY"
    PROJECT = "PROJECT"
    CLIENT = "CLIENT"


class RuleDiscipline(str, enum.Enum):
    """Engineering disciplines for rules"""

    ELECTRICAL = "ELECTRICAL"
    AUTOMATION = "AUTOMATION"
    MECHANICAL = "MECHANICAL"
    PROCESS = "PROCESS"
    PIPING = "PIPING"
    INSTRUMENTATION = "INSTRUMENTATION"


class RuleActionType(str, enum.Enum):
    """Types of actions a rule can perform"""

    CREATE_CHILD = "CREATE_CHILD"  # Create related asset (e.g., motor for pump)
    CREATE_CABLE = "CREATE_CABLE"  # Create cable connection
    CREATE_RELATIONSHIP = "CREATE_RELATIONSHIP"  # Create edge between nodes
    SET_PROPERTY = "SET_PROPERTY"  # Set/update asset properties
    CREATE_PACKAGE = "CREATE_PACKAGE"  # Group assets into package
    ALLOCATE_IO = "ALLOCATE_IO"  # Allocate IO card/terminal
    VALIDATE = "VALIDATE"  # Validation rule (check constraints)


class RuleValidationStatus(str, enum.Enum):
    """Status of the rule's lifecycle"""

    DRAFT = "DRAFT"  # Newly created, only runs in test mode
    DEV_VALIDATED = "DEV_VALIDATED"  # Tested by engineer, safe for dev environment
    PROD_READY = "PROD_READY"  # Approved for production/final generation
    DEPRECATED = "DEPRECATED"  # Do not use


class RuleDefinition(Base):
    """
    Database-driven rule definition.

    Rules are applied in priority order:
    CLIENT (100) > PROJECT (50) > COUNTRY (30) > FIRM (10)

    Example rule:
        {
            "name": "Create motor for centrifugal pumps",
            "source": "FIRM",
            "priority": 10,
            "discipline": "ELECTRICAL",
            "action_type": "CREATE_CHILD",
            "condition": {
                "asset_type": "PUMP",
                "property_filters": [
                    {"key": "pump_type", "op": "==", "value": "CENTRIFUGAL"}
                ]
            },
            "action": {
                "create_child": {
                    "type": "MOTOR",
                    "naming": "{parent_tag}-M",
                    "relation": "powers",
                    "discipline": "ELECTRICAL",
                    "inherit_properties": ["area", "system", "voltage"],
                    "properties": {
                        "motor_type": "Electric",
                        "enclosure": "TEFC"
                    }
                }
            }
        }
    """

    __tablename__ = "rule_definitions"

    # Primary Key
    id = Column(String, primary_key=True, default=lambda: f"rule-{uuid.uuid4().hex[:12]}")

    # Basic Info
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Source & Priority
    source = Column(SQLEnum(RuleSource), nullable=False, index=True)
    source_id = Column(String, nullable=True)  # FK to country/project/client (if applicable)
    priority = Column(Integer, nullable=False, default=10, index=True)

    # Categorization
    discipline = Column(
        String, nullable=True, index=True
    )  # ELECTRICAL, AUTOMATION, MECHANICAL, PROCESS
    category = Column(
        String, nullable=True, index=True
    )  # ASSET_CREATION, CABLE_SIZING, VALIDATION, ELECTRICAL_CODE, etc.
    action_type = Column(SQLEnum(RuleActionType), nullable=False, index=True)

    # Enforcement
    is_enforced = Column(
        Boolean, default=False, index=True
    )  # Non-negotiable rule (e.g., electrical codes)

    # Rule Logic (JSON)
    condition = Column(JSON, nullable=False)
    # Example: {
    #   "asset_type": "PUMP",
    #   "property_filters": [{"key": "pump_type", "op": "==", "value": "CENTRIFUGAL"}]
    # }

    action = Column(JSON, nullable=False)
    # Example: {
    #   "create_child": {
    #     "type": "MOTOR",
    #     "relation": "powers",
    #     "properties": {...}
    #   }
    # }

    # Conflict Tracking
    overrides_rule_id = Column(
        String, ForeignKey("rule_definitions.id"), nullable=True
    )  # Rule this one overrides
    conflicts_with = Column(
        JSON, nullable=True
    )  # List of conflicting rules: [{rule_id: "xxx", reason: "..."}, ...]

    # Metadata
    validation_status = Column(
        SQLEnum(RuleValidationStatus), default=RuleValidationStatus.DRAFT, index=True
    )
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

    # Execution Stats (denormalized for performance)
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime, nullable=True)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)

    # Relationships
    executions = relationship("RuleExecution", back_populates="rule", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<RuleDefinition {self.name} (priority={self.priority}, active={self.is_active})>"


class RuleExecution(Base):
    """
    Audit trail for rule execution.

    Logs every action taken by every rule for complete transparency.
    This allows engineers to understand what the system did and why.
    """

    __tablename__ = "rule_executions"

    # Primary Key
    id = Column(String, primary_key=True, default=lambda: f"exec-{uuid.uuid4().hex[:12]}")

    # Context
    rule_id = Column(String, ForeignKey("rule_definitions.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    asset_id = Column(String, nullable=True, index=True)  # Asset the rule acted on (if applicable)

    # Execution Result
    action_type = Column(String, nullable=False)  # CREATE, LINK, SKIP, ERROR, UPDATE
    action_taken = Column(Text, nullable=False)  # Human-readable description

    # Technical Details
    condition_matched = Column(Boolean, default=False)
    created_entity_id = Column(String, nullable=True)  # ID of created asset/edge/cable
    created_entity_type = Column(String, nullable=True)  # "MOTOR", "CABLE", "EDGE"

    # Performance Tracking
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    execution_time_ms = Column(Integer, nullable=True)  # Execution time in milliseconds

    # Error Handling
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)

    # Relationships
    rule = relationship("RuleDefinition", back_populates="executions")
    project = relationship("Project")

    def __repr__(self):
        return f"<RuleExecution {self.action_type} at {self.timestamp}>"


# Backward compatibility aliases
ActionType = RuleActionType
