import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class PackageStatus(str, enum.Enum):
    OPEN = "OPEN"
    ISSUED = "ISSUED"
    CLOSED = "CLOSED"


class Package(Base):
    __tablename__ = "packages"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)

    # Package type for export templates (IN-P040, CA-P040, etc.)
    package_type = Column(String, nullable=True)

    # Metadata for template rendering (discipline, revision, area, etc.)
    package_metadata = Column(JSON, nullable=True)

    status = Column(Enum(PackageStatus), default=PackageStatus.OPEN)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project")
    assets = relationship("Asset", back_populates="package")
