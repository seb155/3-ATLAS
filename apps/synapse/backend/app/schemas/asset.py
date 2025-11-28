from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AssetType(str, Enum):
    INSTRUMENT = "INSTRUMENT"
    MOTOR = "MOTOR"
    VALVE = "VALVE"
    CONTROL_SYSTEM = "CONTROL_SYSTEM"
    PUMP = "PUMP"
    TANK = "TANK"


class IOType(str, Enum):
    AI = "AI"
    AO = "AO"
    DI = "DI"
    DO = "DO"
    PROFIBUS = "PROFIBUS"
    ETHERNET = "ETHERNET"
    HARDWIRED = "HARDWIRED"
    PROFINET = "PROFINET"
    ETHERNET_IP = "ETHERNET_IP"
    MODBUS_TCP = "MODBUS_TCP"


class AssetDataStatusEnum(str, Enum):
    """Status of the asset's data completeness"""

    FRESH_IMPORT = "FRESH_IMPORT"
    IN_REVIEW = "IN_REVIEW"
    VALIDATED = "VALIDATED"
    ERROR = "ERROR"


class AssetBase(BaseModel):
    tag: str
    description: str | None = None
    type: str  # Changed from Enum to String for flexibility (unified model)
    area: str | None = None
    system: str | None = None
    io_type: IOType | None = Field(None, alias="ioType")
    mechanical: dict[str, Any] | None = None
    electrical: dict[str, Any] | None = None
    process: dict[str, Any] | None = None
    purchasing: dict[str, Any] | None = None
    manufacturer_part_id: str | None = Field(None, alias="manufacturerPartId")
    location_id: str | None = Field(None, alias="locationId")
    data_status: AssetDataStatusEnum | None = Field(
        default=AssetDataStatusEnum.FRESH_IMPORT, alias="dataStatus"
    )

    @field_validator("electrical")
    @classmethod
    def validate_electrical(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        if v:
            voltage = v.get("voltage")
            if voltage:
                # Normalize voltage string (remove spaces, lowercase) for check
                norm_v = str(voltage).lower().replace(" ", "")
                allowed = ["120v", "240v", "480v", "600v", "4160v", "24vdc", "120vac"]
                if norm_v not in allowed:
                    # We allow it but maybe warn? For now let's enforce it strictly as per plan
                    # Or better, just check if it ends with V or VDC/VAC
                    pass
                    # Actually, let's stick to the plan:
                    # "Validate voltage levels against a standard list"
                    # But given the user might type anything, let's be flexible
                    # or just strict on common ones.
                    # Let's enforce a list for now to demonstrate validation.
                    if norm_v not in allowed:
                        raise ValueError(
                            f"Invalid voltage: {voltage}. Allowed: {', '.join(allowed)}"
                        )
        return v

    @field_validator("process")
    @classmethod
    def validate_process(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        if v:
            min_val = v.get("minRange")
            max_val = v.get("maxRange")
            if min_val is not None and max_val is not None:
                try:
                    min_f = float(min_val)
                    max_f = float(max_val)
                except (ValueError, TypeError):
                    # If values are not numbers, we can't compare ranges.
                    # We could raise an error or just ignore. For now, ignore.
                    return v

                if min_f >= max_f:
                    raise ValueError("minRange must be less than maxRange")
        return v


class AssetCreate(AssetBase):
    id: str | None = None


class AssetUpdate(AssetBase):
    tag: str | None = None
    type: AssetType | None = None
    data_status: AssetDataStatusEnum | None = Field(None, alias="dataStatus")


class AssetBulkUpdateItem(AssetUpdate):
    id: str


class AssetResponse(AssetBase):
    id: str
    project_id: str

    model_config = {"from_attributes": True, "populate_by_name": True, "serialize_by_alias": True}
