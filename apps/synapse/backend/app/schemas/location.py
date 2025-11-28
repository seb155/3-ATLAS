from enum import Enum

from pydantic import BaseModel, Field


class LocationType(str, Enum):
    SITE = "SITE"
    AREA = "AREA"
    EHOUSE = "EHOUSE"
    ROOM = "ROOM"
    CABINET = "CABINET"
    JUNCTION_BOX = "JUNCTION_BOX"


class LBSNodeBase(BaseModel):
    name: str
    type: LocationType
    parent_id: str | None = Field(None, alias="parentId")
    capacity_slots: int | None = Field(None, alias="capacitySlots")
    design_heat_dissipation: float | None = Field(None, alias="designHeatDissipation")
    ip_rating: str | None = Field(None, alias="ipRating")


class LBSNodeCreate(LBSNodeBase):
    id: str | None = None


class LBSNodeUpdate(LBSNodeBase):
    name: str | None = None
    type: LocationType | None = None


class LBSNodeResponse(LBSNodeBase):
    id: str
    project_id: str
    # children: List['LBSNodeResponse'] = []

    model_config = {"from_attributes": True, "populate_by_name": True, "serialize_by_alias": True}
