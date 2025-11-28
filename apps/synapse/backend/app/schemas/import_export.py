"""
Pydantic schemas for CSV import/export operations.
"""
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class CSVRowError(BaseModel):
    """Error information for a failed CSV row"""
    row: int = Field(..., description="Row number (0-indexed)")
    tag: Optional[str] = Field(None, description="Asset tag if available")
    error: str = Field(..., description="Error message")


class ImportSummaryResponse(BaseModel):
    """Response schema for CSV import operations"""
    success: bool = Field(..., description="Overall operation success")
    total_rows: int = Field(..., description="Total rows processed")
    created: int = Field(default=0, description="Number of assets created")
    updated: int = Field(default=0, description="Number of assets updated")
    failed: int = Field(default=0, description="Number of rows that failed")
    errors: list[CSVRowError] = Field(default_factory=list, description="List of errors")

    # Rule execution results (optional)
    rules_executed: Optional[int] = Field(None, description="Number of rules executed")
    child_assets_created: Optional[int] = Field(None, description="Child assets created by rules")
    rule_execution_time_ms: Optional[int] = Field(None, description="Rule execution time in milliseconds")
    rule_execution_error: Optional[str] = Field(None, description="Rule execution error message")

    model_config = {"from_attributes": True}


class CSVRowSchema(BaseModel):
    """Schema for validating individual CSV row data"""
    tag: str = Field(..., min_length=1, max_length=100, description="Asset tag (required)")
    type: str = Field(..., min_length=1, description="Asset type (required for new assets)")
    description: Optional[str] = Field(None, max_length=500, description="Asset description")
    area: Optional[str] = Field(None, max_length=100, description="Functional breakdown area")
    system: Optional[str] = Field(None, max_length=100, description="System identifier")
    io_type: Optional[str] = Field(None, description="IO type (AI, AO, DI, DO, etc.)")
    manufacturer_part_id: Optional[str] = Field(None, max_length=100, description="Manufacturer part number")
    location_id: Optional[str] = Field(None, description="Location ID (LBS)")

    # Nested fields
    electrical: Optional[dict[str, Any]] = Field(default_factory=dict, description="Electrical properties")
    process: Optional[dict[str, Any]] = Field(default_factory=dict, description="Process properties")
    purchasing: Optional[dict[str, Any]] = Field(default_factory=dict, description="Purchasing properties")

    @field_validator("tag")
    @classmethod
    def validate_tag(cls, v: str) -> str:
        """Validate tag format"""
        if not v or not v.strip():
            raise ValueError("Tag cannot be empty or whitespace")
        # Remove extra whitespace
        return v.strip()

    @field_validator("electrical")
    @classmethod
    def validate_electrical(cls, v: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        """Validate electrical properties"""
        if v and "voltage" in v:
            voltage = str(v["voltage"]).lower().replace(" ", "")
            # List of common voltages (can be extended)
            allowed_voltages = ["120v", "240v", "480v", "600v", "4160v", "24vdc", "120vac", "240vac", "480vac"]
            # Allow any voltage that ends with V, VDC, or VAC
            if not (voltage.endswith("v") or voltage.endswith("vdc") or voltage.endswith("vac")):
                raise ValueError(f"Invalid voltage format: {v['voltage']}. Must end with V, VDC, or VAC")

        if v and "powerKW" in v:
            try:
                power = float(v["powerKW"])
                if power < 0:
                    raise ValueError("Power (kW) must be non-negative")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid power value: {v['powerKW']}. Must be a number")

        return v

    @field_validator("process")
    @classmethod
    def validate_process(cls, v: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        """Validate process properties"""
        if v:
            min_range = v.get("minRange")
            max_range = v.get("maxRange")

            if min_range is not None and max_range is not None:
                try:
                    min_val = float(min_range)
                    max_val = float(max_range)
                    if min_val >= max_val:
                        raise ValueError("minRange must be less than maxRange")
                except (ValueError, TypeError) as e:
                    if "minRange must be less than maxRange" in str(e):
                        raise
                    # Invalid number format
                    raise ValueError(f"Invalid range values: minRange={min_range}, maxRange={max_range}")

        return v

    model_config = {"from_attributes": True, "populate_by_name": True}
