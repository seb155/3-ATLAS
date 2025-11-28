"""
Pydantic Schemas for Rule Management

Defines request/response schemas for the Rule API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class RuleSourceEnum(str, Enum):
    """Rule source types"""

    FIRM = "FIRM"
    COUNTRY = "COUNTRY"
    PROJECT = "PROJECT"
    CLIENT = "CLIENT"


class RuleActionTypeEnum(str, Enum):
    """Rule action types"""

    CREATE_CHILD = "CREATE_CHILD"
    CREATE_CABLE = "CREATE_CABLE"
    CREATE_RELATIONSHIP = "CREATE_RELATIONSHIP"
    SET_PROPERTY = "SET_PROPERTY"
    CREATE_PACKAGE = "CREATE_PACKAGE"
    ALLOCATE_IO = "ALLOCATE_IO"
    VALIDATE = "VALIDATE"


class RuleValidationStatusEnum(str, Enum):
    """Rule validation status"""

    DRAFT = "DRAFT"
    DEV_VALIDATED = "DEV_VALIDATED"
    PROD_READY = "PROD_READY"
    DEPRECATED = "DEPRECATED"


# ============================================================================
# Request Schemas (for creating/updating rules)
# ============================================================================


class RuleCondition(BaseModel):
    """
    Rule condition schema.

    Defines when a rule should be applied to an asset.
    """

    asset_type: str | None = None  # "PUMP", "MOTOR", etc.
    node_type: str | None = None  # "AREA", "SITE", etc.
    property_filters: list[dict[str, Any]] = Field(default_factory=list)
    # Example: [{"key": "voltage", "op": "==", "value": "600V"}]

    class Config:
        schema_extra = {
            "example": {
                "asset_type": "PUMP",
                "property_filters": [{"key": "pump_type", "op": "==", "value": "CENTRIFUGAL"}],
            }
        }


class RuleAction(BaseModel):
    """
    Rule action schema.

    Defines what the rule should do when condition matches.
    """

    create_child: dict[str, Any] | None = None
    create_cable: dict[str, Any] | None = None
    create_relationship: dict[str, Any] | None = None
    set_property: dict[str, Any] | None = None
    create_package: dict[str, Any] | None = None

    class Config:
        schema_extra = {
            "example": {
                "create_child": {
                    "type": "MOTOR",
                    "naming": "{parent_tag}-M",
                    "relation": "powers",
                    "discipline": "ELECTRICAL",
                    "inherit_properties": ["area", "system"],
                    "properties": {"motor_type": "Electric", "enclosure": "TEFC"},
                }
            }
        }


class RuleCreate(BaseModel):
    """Schema for creating a new rule"""

    name: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    source: RuleSourceEnum
    source_id: str | None = None
    priority: int | None = Field(default=None, ge=1, le=100)
    discipline: str | None = None
    action_type: RuleActionTypeEnum
    condition: dict[str, Any]
    action: dict[str, Any]
    validation_status: RuleValidationStatusEnum = RuleValidationStatusEnum.DRAFT
    is_active: bool = True

    @validator("priority", always=True)
    def set_default_priority(cls, v, values):
        """Auto-assign priority based on source if not provided"""
        if v is not None:
            return v

        # Default priorities by source
        source_priorities = {
            RuleSourceEnum.FIRM: 10,
            RuleSourceEnum.COUNTRY: 30,
            RuleSourceEnum.PROJECT: 50,
            RuleSourceEnum.CLIENT: 100,
        }

        source = values.get("source")
        return source_priorities.get(source, 10)

    class Config:
        schema_extra = {
            "example": {
                "name": "Create motor for pumps",
                "description": "All pumps require a motor driver",
                "source": "FIRM",
                "priority": 10,
                "discipline": "ELECTRICAL",
                "action_type": "CREATE_CHILD",
                "condition": {"asset_type": "PUMP"},
                "action": {
                    "create_child": {
                        "type": "MOTOR",
                        "naming": "{parent_tag}-M",
                        "relation": "powers",
                        "discipline": "ELECTRICAL",
                        "inherit_properties": ["area", "system"],
                    }
                },
                "is_active": True,
            }
        }


class RuleUpdate(BaseModel):
    """Schema for updating a rule"""

    name: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = None
    is_active: bool | None = None
    condition: dict[str, Any] | None = None
    action: dict[str, Any] | None = None
    validation_status: RuleValidationStatusEnum | None = None


# ============================================================================
# Response Schemas
# ============================================================================


class RuleResponse(BaseModel):
    """Schema for rule responses"""

    id: str
    name: str
    description: str | None
    source: str
    source_id: str | None
    priority: int
    discipline: str | None
    action_type: str
    condition: dict[str, Any]
    action: dict[str, Any]
    validation_status: RuleValidationStatusEnum
    is_active: bool
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    version: int
    execution_count: int
    success_count: int
    failure_count: int
    last_executed_at: datetime | None

    class Config:
        from_attributes = True


class RuleListResponse(BaseModel):
    """Schema for paginated rule list"""

    total: int
    page: int
    page_size: int
    rules: list[RuleResponse]


# ============================================================================
# Rule Execution Schemas
# ============================================================================


class RuleExecutionResponse(BaseModel):
    """Schema for rule execution audit log"""

    id: str
    rule_id: str
    rule_name: str | None = None  # Joined from rule
    project_id: str
    asset_id: str | None
    action_type: str
    action_taken: str
    condition_matched: bool
    created_entity_id: str | None
    created_entity_type: str | None
    timestamp: datetime
    execution_time_ms: int | None
    error_message: str | None

    class Config:
        from_attributes = True


class RuleTestRequest(BaseModel):
    """Schema for testing a rule on sample data"""

    sample_assets: list[dict[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "sample_assets": [
                    {
                        "tag": "310-PP-001",
                        "type": "PUMP",
                        "properties": {"pump_type": "CENTRIFUGAL"},
                    },
                    {"tag": "310-TK-001", "type": "TANK"},
                ]
            }
        }


class RuleTestResult(BaseModel):
    """Result for a single asset test"""

    asset_tag: str
    condition_matched: bool
    would_create: str | None = None
    would_set: dict[str, Any] | None = None
    reason: str | None = None


class RuleTestResponse(BaseModel):
    """Schema for rule test results"""

    rule_id: str
    rule_name: str
    test_results: list[RuleTestResult]

    class Config:
        schema_extra = {
            "example": {
                "rule_id": "rule-abc123",
                "rule_name": "Create motor for pumps",
                "test_results": [
                    {
                        "asset_tag": "310-PP-001",
                        "condition_matched": True,
                        "would_create": "310-PP-001-M (MOTOR)",
                        "reason": "Asset type matches 'PUMP'",
                    },
                    {
                        "asset_tag": "310-TK-001",
                        "condition_matched": False,
                        "reason": "Asset type 'TANK' does not match 'PUMP'",
                    },
                ],
            }
        }


class RuleExecuteRequest(BaseModel):
    """Request schema for executing a single rule"""

    asset_ids: list[str] | None = None
    project_id: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "asset_ids": ["uuid-1", "uuid-2", "uuid-3"],
                "project_id": "northern-crusher-plant",
            }
        }


class RuleExecutionSummary(BaseModel):
    """Summary of rule execution"""

    total_rules: int
    total_assets: int
    total_executions: int
    actions_taken: int
    skipped: int
    errors: int
    time_elapsed_ms: int

    class Config:
        schema_extra = {
            "example": {
                "total_rules": 15,
                "total_assets": 50,
                "total_executions": 75,
                "actions_taken": 45,
                "skipped": 28,
                "errors": 2,
                "time_elapsed_ms": 3450,
            }
        }
