from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.database import Base


class Asset(Base):  # Define an affected incident asset.
    __tablename__ = "incident_assets"  # Map the model to the asset table.

    id = Column(Integer, primary_key=True)  # Store the asset identifier.
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)  # Link the asset to an incident.
    asset_name = Column(String, nullable=False)  # Store the asset name.
    asset_type = Column(String)  # Store the asset type.
    created_at = Column(  # Define the asset creation timestamp.
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
